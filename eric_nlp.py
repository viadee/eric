from dictionary import dictionary
import numpy as np
import string
import fasttext
import scipy
from scipy import spatial

d = {
    "class": {
        "feature-type": "categorical",
        "values": {
            0: "died",
            1: "survived"
        },
        "data-type": "string"
    },
    "Pclass": {
        "feature-type": "categorical",
        "values": {
            0: "First",
            1: "Second",
            2: "Third"
        },
        "data-type": "string"
    },
    "Sex": {
        "feature-type": "categorical",
        "values": {
            0: "Male",
            1: "Female"
        },
        "data-type": "string"
    },
    "Age": {
        "feature-type": "continuous",
        "regex": "(\\d+)",
        "values": {"min": 0, "max": 90},
        "data-type": "integer"
    },
    "Fare": {
        "feature-type": "continuous",
        "regex": "(\\d+)(\\.\\d+)?",
        "values": {"min": 0, "max": 512},
        "data-type": "float"
    },
    "Embarked": {
        "feature-type": "categorical",
        "values": {
            0: "Southampton",
            1: "Cherbourg",
            2: "Queenstown"
            },
        "data-type": "string"
    },
    "Relatives": {
        "feature-type": "continuous",
        "regex": "(\\d+)",
        "values": {"min": 0, "max": 10},
        "data-type": "integer"
    }
}


###
# CHANGE LATER
###
'''
self.best_matches_all_methods -> delete
self.best_matches -> not self
map_to_eric_function() -> return ret_val (returns ranking right now)
import model_columns in Eric_nlp.__init__()
'''

###
#  NLP CLASS
###
class Eric_nlp():
  def __init__(self, model_file = "data\\cc.en.300.bin"):
    #"last_..." variables get set from outside of class
    self.deny_id = "none"
    self.deny_threshold = 0.62
    self.last_valid_answers = ""
    self.last_clips_type = ""
    self.last_value_asked = ""
    self.original_message = ""
    self.model_columns = d
    self.best_matches = dict()
    self.best_matches_all_methods = dict()
    self.placeholders = dict()#{'<key>': {'age': '23'}, '<outcome>': 'died'}
    self.bad_input = True
    self.init_key_sentences()#key: function-id, value: list of strings
    self.stop_chars = list(string.punctuation)
    self.ft = fasttext.load_model(model_file)

  #reads all key sentences for functions and stores them in the calling object's attribute key_sentences
  def init_key_sentences(self):
    self.key_sentences = dict()
    for d in dictionary:
      self.key_sentences[d["id"]] = d["key_sentences"]
  
  #take a message string and return the id of the function in dictionary.dictionary that is most likely corresponding to the message
  def map_to_eric_function(self, message, method="cosine", limit=2):
    self.bad_input = True #only set to False if sufficiently probable match was found
    self.original_message = message

    message = self.preprocess_input(message)    
    ranking = self.get_similarity_ranking(message, method=method, limit=limit)
    ranking = self.prostprocessing(ranking)

    return ranking

  #create comparison of ranking and return list of strings that can be printed to file or console
  def method_comparison(self, input_str, method="cosine", limit=5):
    ret_val = [input_str]
    ranking = self.map_to_eric_function(input_str, method=method, limit=limit)
    choice = ranking[0]
    if len(ranking) >= 2:
      certainty = (ranking[0][1] - ranking[1][1]) * 100
    else:
      certainty = -1.0

    first = True
    out_lines = [["function_id", "<CALCULATED>"]]
    for fct_id, similarity in ranking:
      one_line = [fct_id, f"{similarity}"]
      for k, v in self.best_matches_all_methods[fct_id].items():
        if first:
          if k == method:
            out_lines[0].append(f"<{k.upper()}>")
          else:
            out_lines[0].append(k)
        one_line.append(f"{v}")
      out_lines.append(one_line)
      first = False

    ret_val.extend(get_pretty_printed_columns(out_lines, align="l"))
    return choice, certainty, ret_val



  #preprocess message (e.g. remove punctuation, all lower case)
  def preprocess_input(self, strng):
    preprocessed_string = remove_chars(strng, self.stop_chars)
    return preprocessed_string.lower()

  #preprocess the string to compare with (e.g. remove punctuation, all lower case, replace placeholders with values from the input)
  def preprocess_key_sentence(self, compare_strng):
    tmp_stop_chars = [x for x in self.stop_chars if x not in ["<", ">"]]
    preprocessed_string = remove_chars(compare_strng, tmp_stop_chars).lower()
    #list of tupels (model_column, column_value)
    keys_values = list(self.placeholders["<key>"].items())

    #if replacements are saved, use them
    if self.placeholders["<outcome>"] is not None:
      outcome = self.placeholders["<outcome>"]
      #print(f"replacing <outcome> with {outcome}")
      preprocessed_string = preprocessed_string.replace("<outcome>", outcome, 1)
    if self.placeholders["<key>"]:
      #go through string and replace keys and values. always replace only one occurence and increase index
      max_index = len(keys_values)
      key_index = 0
      value_index = 0
      tmp_string = preprocessed_string
      for word in tmp_string.split():
        if word == "<key>" and key_index < max_index:
          replacement = keys_values[key_index][0]
          #if corresponding value is None, skip value
          if keys_values[key_index][1] is None:
            value_index += 1
          key_index += 1
          #print(f"replacing <key> with {replacement}")
          preprocessed_string = preprocessed_string.replace("<key>", replacement, 1)
        elif word == "<value>" and value_index < max_index:
          replacement = keys_values[value_index][1]
          value_index += 1
          #print(f"replacing <value> with {replacement}")
          if replacement:
            preprocessed_string = preprocessed_string.replace("<value>", replacement, 1)
      #if to every key there wasn't always a value to be replaced, return the original sentence.
      #that occures for example with "what if age was greater/lesser" and we shouldn't give that key_sentence
      #an extra word (here "age") to match with the input
      if key_index != value_index:
        print(f"different indices: returning '{tmp_string}' instead of '{preprocessed_string}'")
        preprocessed_string = compare_strng

    return preprocessed_string

  #postprocess ranking (e.g. dependency parsing)
  def prostprocessing(self, ranking):
    return ranking

  '''
  go through string word by and see if you can find replacements for placeholders
  return None but saves everything in object's attribute self.placeholders
    key: placeholders as they occur in dictionary.dictionary. as of now these are <key>, <outcome>
    value:  if key==<outcome>: one of the values of server.d["class"]["values"]
            if key==<key>: another dict with 
              key: column name (of model) that was found in input
              value: value for that column name if found in input
  '''
  def extract_placeholders(self, strng):
    self.placeholders = {"<key>": dict(), "<outcome>": None}
    words = self.preprocess_input(strng).split()
    for word, index in zip(words, range(len(words))):
      #if word is a value the outcome can take, save it as <outcome>, else look if it matches a column name
      if word in self.model_columns["class"]["values"].values():
        self.placeholders["<outcome>"] = word
      elif word != "class" and word.capitalize() in self.model_columns.keys():
        value = self.extract_value(word.capitalize(), words[index+1:])
        self.placeholders["<key>"][word] = value

  #only called from extract_placeholders. takes rest of sentence as list of words
  #returns first occurence of a fitting value. None if none was found
  def extract_value(self, key, word_list):
    #categorical values
    if self.model_columns[key]["feature-type"] == "categorical":
      possible_values = [x.lower() for x in self.model_columns[key]["values"].values()]
      for w in word_list:
        if w in possible_values:
          return w
    #continuous values
    elif self.model_columns[key]["feature-type"] == "continuous":
      min = self.model_columns[key]["values"]["min"]
      max = self.model_columns[key]["values"]["max"]
      for w in word_list:
        try:
          as_number = float(w)
          # if as_number >= min and as_number <= max:
          return w
        except ValueError:
          pass
    return None



  #return vector representation of sentence (for now only fasttext is used)
  def get_sentence_vector(self, msg):
    return self.ft.get_sentence_vector(msg)

  #takes message and returns the id of the top <limit> functions in dictionary.dictionary that are most similiar to the message
  def get_similarity_ranking(self, input_message, method="cosine", limit=2, normalise = False):
    self.extract_placeholders(input_message)
    input_vector = self.get_sentence_vector(input_message)
    if normalise:
      input_vector = normalise_vector(input_vector)


    #go through all eric-functions and their key_sentences
    self.best_matches = dict()
    self.best_matches_all_methods = dict()
    for function_id, list_of_key_sentences in self.key_sentences.items():
      for key_sentence in list_of_key_sentences:
        #tmp_stop_chars = [x for x in self.stop_chars if x not in ["<", ">"]]
        #asdf = remove_chars(key_sentence, tmp_stop_chars).lower()
        key_sentence = self.preprocess_key_sentence(key_sentence)
        #if asdf != key_sentence:
          #print(f"( old / new ): ( '{asdf}' / '{key_sentence}' )")
        compare_vector = self.get_sentence_vector(key_sentence)
        '''
        braycurtis       -- the Bray-Curtis distance.
        canberra         -- the Canberra distance.
        chebyshev        -- the Chebyshev distance.
        cityblock        -- the Manhattan distance.
        correlation      -- the Correlation distance.
        cosine           -- the Cosine distance.
        euclidean        -- the Euclidean distance.
        jensenshannon    -- the Jensen-Shannon distance.
        mahalanobis      -- the Mahalanobis distance.
        minkowski        -- the Minkowski distance.
        seuclidean       -- the normalized Euclidean distance.
        sqeuclidean      -- the squared Euclidean distance.
        '''

        #these are DISTANCES, similarity is only in the variables <sim>, <best_matches>, and <best_matches_all_methods>
        distances = dict()
        distances["braycurtis"] = scipy.spatial.distance.braycurtis(input_vector,compare_vector)
        #distances["canberra"] = scipy.spatial.distance.canberra(input_vector,compare_vector)
        distances["chebyshev"] = scipy.spatial.distance.chebyshev(input_vector,compare_vector)
        #distances["cityblock"] = scipy.spatial.distance.cityblock(input_vector,compare_vector)
        distances["correlation"] = scipy.spatial.distance.correlation(input_vector,compare_vector)
        distances["cosine"] = scipy.spatial.distance.cosine(input_vector,compare_vector)
        distances["euclidean"] = scipy.spatial.distance.euclidean(input_vector,compare_vector)
        #distances["jensenshannon"] = scipy.spatial.distance.jensenshannon(input_vector,compare_vector)
        #distances["mahalanobis"] = scipy.spatial.distance.mahalanobis(input_vector,compare_vector)
        distances["minkowski"] = scipy.spatial.distance.minkowski(input_vector,compare_vector)
        #distances["seuclidean"] = scipy.spatial.distance.seuclidean(input_vector,compare_vector)
        distances["sqeuclidean"] = scipy.spatial.distance.sqeuclidean(input_vector,compare_vector)
        sim = 1.0 - distances[method]

        #multiple key sentences per function get compared. only save the best of those
        update_methods = False
        if function_id in self.best_matches.keys():
            if self.best_matches[function_id] < sim:
                self.best_matches[function_id] = sim
                update_methods = True
        else:
            self.best_matches[function_id] = sim
            update_methods = True

        if update_methods:
          self.best_matches_all_methods[function_id] = dict()
          self.best_matches_all_methods[function_id]["braycurtis"] = (1.0 - distances["braycurtis"]) * 100
          #self.best_matches_all_methods[function_id]["canberra"] = distances["canberra"]
          self.best_matches_all_methods[function_id]["chebyshev"] = (1.0 - distances["chebyshev"]) * 100
          #self.best_matches_all_methods[function_id]["cityblock"] = distances["cityblock"]
          self.best_matches_all_methods[function_id]["correlation"] = (1.0 - distances["correlation"]) * 100
          self.best_matches_all_methods[function_id]["cosine"] = (1.0 - distances["cosine"]) * 100
          self.best_matches_all_methods[function_id]["euclidean"] = (1.0 - distances["euclidean"]) * 100
          #self.best_matches_all_methods[function_id]["jensenshannon"] = distances["jensenshannon"]
          #self.best_matches_all_methods[function_id]["mahalanobis"] = (1.0 - distances["mahalanobis"]) * 100
          self.best_matches_all_methods[function_id]["minkowski"] = (1.0 - distances["minkowski"]) * 100
          #self.best_matches_all_methods[function_id]["seuclidean"] = (1.0 - distances["seuclidean"]) * 100
          self.best_matches_all_methods[function_id]["sqeuclidean"] = (1.0 - distances["sqeuclidean"]) * 100

    
    top_matches = {key: val for key, val in sorted(self.best_matches.items(), key=lambda item: item[1], reverse=True)}
    top_matches = list(top_matches.items())
    
    #return only top <limit> items
    if limit > 0 and limit < len(top_matches):
      top_matches = top_matches[:limit]

    return top_matches


###
#  STATIC FUNCTIONS
###

#takes numpy array and normalises it
def normalise_vector(vec):
    norm=np.linalg.norm(vec)
    if norm == 0: 
       return vec
    return vec/norm

#removes multiple different chars from a string
def remove_chars(strg, chars_to_remove):
  removal_dict = {key: "" for key in chars_to_remove}
  return replace_chars(strg, removal_dict)

#return a list of strings the two lists of strings have in common
def words_in_common(str1, str2):
  return [x for x in str1 if x in str2]

#replacements is a dict. every occurence of a key in sentence gets replaced with replacements[key]
def replace_chars(sentence, replacements):
  new_sentence = ""
  for w in sentence:
    if w in replacements.keys():
      new_sentence += replacements[w]
    else:
      new_sentence += w
  
  return new_sentence

#takes a list of lists with data in it to print it in evenly spaced columns
#aligns columns right ("r"), left ("l") or else centered
def get_pretty_printed_columns(data, align = "r", padding = 3):
  col_width = max(len(word) for row in data for word in row) + padding
  ret_val = []
  if align == "r":
    for row in data:
      one_line = "".join(word.rjust(col_width) for word in row)
      ret_val.append(one_line)
  elif align == "l":
    for row in data:
      one_line = "".join(word.ljust(col_width) for word in row)
      ret_val.append(one_line)
  else:
    for row in data:
      one_line = "".join(word.center(col_width) for word in row)
      ret_val.append(one_line)
  return ret_val