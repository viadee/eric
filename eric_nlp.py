from dictionary import dictionary, nlp_dictionary, reserved_placeholder_words
import numpy as np
import depparse
import string
import fasttext
import scipy
import re
from scipy import spatial

d = {
    "class": {
        "feature-type": "categorical",
        "values": {
            0: "died",
            1: "survived"
        },
        "phrasings": {
          "died": ["die", "dies"],
          "survived": ["survive", "survives"]
        },
        "lemmas": {
          "died": "die",
          "survived": "survive"
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
  def __init__(self):
    self.ft = None #model needs to be loaded separately
    self.stanza_pipeline = None #loaded separately
    self.model = ""
    self.method = "minkowski" #default method
    self.language = "en"
    self.deny_id = "none"
    self.deny_threshold = 0.68#0.62 #below this value, eric says, he does not understand the message
    self.depparse_threshold = 0.8 #if the best similarity gets below this value, depparsing is used to increase certainty
    self.valid_answers = ""
    self.normalise_embedding = False
    self.model_columns = d
    self.best_matches = dict()
    self.best_matches_all_methods = dict()
    self.placeholders = dict()#{'<key>': {'age': '23'}, '<outcome>': 'died'}
    self.search_for_placeholder_values = True #if true, extract_placeholders() will look for model values even if no model name was found in the input
    self.bad_input = True
    self.prioritise_negation = True #if two depparse templates match some input, the negated one is preferred
    self.init_key_sentences()#key: function-id, value: list of strings
    self.accepted_special_chars = ["=", "<", ">"]
    self.stop_chars = [x for x in list(string.punctuation) if x != "'" and x not in self.accepted_special_chars]
    self.yes_phrasings = ["yes", "y", "yay", "yas", "ja", "sure", "ok", "okay", "k", "kk", "of course", "go ahead", "continue"]
    self.no_phrasings = ["nay", "no", "n", "nah", "negative", "nope", "never", "stop"]
    self.subject_phrasings = [#phrasings of the "subject" to which the outcome applies to. With titanic for example these are persons for which the outcome can be "died" or "survived"
      "the person",
      "a person",
      "person",
      "the passenger",
      "a passenger",
      "passenger"
      "someone",
      "they",
      "them"
    ]
    self.pronouns = [
      "i", "me", "my",
      "you", "your",
      "he", "his", "him",
      "she", "her",
      "it",
      "we",
      "they", "them"
    ]
    self.non_semantic_words = [
      "the"
    ]
    self.stop_words = [
      "please"
    ]
    self.general_replacements = {
      "’": "'",
      "n't": " not",
    }
    self.model_specific_replacements = {
      "first class": "first pclass",
      "second class": "second pclass",
      "third class": "third pclass"
    }
    self.preprocessing_methods = {
      "ssc": (True, "Space out accepted_special_chars"), #e.g. makes ">55" become " > 55 "
      "rcp": (True, "Replace critical phrasings"),
      "rms": (True, "Replace Model specific phrasings"),
      "rsc": (True, "Remove stop chars"),
      "rnw": (False, "Remove non-semantic words"), #--> does not make any difference
      "rp": (False, "Remove pronouns"),#--> makes the result worse
      "rsw": (True, "Remove stop words"), #words that don't do anything
      "lc": (True, "Lower case"),
      "plh": (True, "Replace placeholders in key sentences")
    }

  def load_model(self, model_file):
    #"data\\cc.en.300.bin"
    print(f"loading FastText model from '{model_file}'")
    self.ft = fasttext.load_model(model_file)
    self.model = model_file
    print("FastText model successfully loaded")

  def init_depparsing(self, language):
    self.stanza_pipeline = depparse.init_stanza(language)

  #reads all key sentences for functions and stores them in the calling object's attribute key_sentences
  def init_key_sentences(self):
    self.key_sentences = dict()
    for d in nlp_dictionary:
      self.key_sentences[d["id"]] = d["key_sentences"]
  
  #take a message string and return the id of the function in dictionary.dictionary that is most likely corresponding to the message
  def map_to_eric_function(self, message):
    self.bad_input = True #only set to False if sufficiently probable match was found
    self.original_message = message

    preprocessed = self.preprocessing(message, "usr_input")
    
    match = self.get_function_match(preprocessed)
    #ranking = self.prostprocessing(ranking)


    return match
  
  def is_valid_answer(self, message):
    if self.valid_answers["type"] == "regex":
      if re.match(self.valid_answers["value"], message):
        print(f"matched '{message}' to '{self.valid_answers['value']}'")
        return True
    elif self.valid_answers["type"] == "selection":
      valid_answers_lower = [x.lower() for x in self.valid_answers["value"]]
      if message.lower() in valid_answers_lower:
        print(f"matched '{message}' to '{valid_answers_lower}'")
        return True
    else:
      print(f"ERROR: unknown answer type: {self.valid_answers}")
  
    print(f"could not match '{message}' to '{self.valid_answers}'")
    return False

  def get_function_match(self, sentence):
    if not self.ft:
      print("ERROR: No model loaded for eric_nlp object")
      return
    if not self.stanza_pipeline:
      self.stanza_pipeline = depparse.init_stanza(self.language)
    
    #tuple (fct_id, similarity in percent)
    similarity_result = self.get_similarity_result(sentence)

    result = similarity_result[0]
    if similarity_result[1] < self.depparse_threshold:
        prepped_sentence = self.preprocessing(sentence, "usr_input")
        tree = self.stanza_pipeline(prepped_sentence).sentences[0]
        depparse_ranking = depparse.get_matching_dictionary_trees(tree, self)
        try:
            if len(depparse_ranking) == 0:
                depparse_result = ("none", [])
            else:
                #tuple (fct_id, matching tree template)
                depparse_result = (depparse_ranking[0][0], depparse_ranking[0][1])
                result = depparse_result[0]
        except:
            print("could not work with depparse ranking:")
            print(depparse_ranking)
            quit()
    else:
        depparse_result = ("none", [f"No depparsing necessary; similarity >= depparse_threshold ({similarity_result[1]} >= {self.depparse_threshold})"])

    if depparse_result[0] == "none" and similarity_result[1] < self.deny_threshold:
        result = "none"

    return result

  #returns tuple (fct_id, similarity in percent) or list of them
  def get_similarity_result(self, sentence, limit=1, gold="no gold given"):
    input_vector = self.get_sentence_vector(sentence)
    if self.normalise_embedding:
      input_vector = normalise_vector(input_vector)

    #go through all eric-functions and their key_sentences
    self.best_matches = dict()
    self.best_matches_all_methods = dict()
    for function_id, list_of_key_sentences in self.key_sentences.items():
      for ks in list_of_key_sentences:
        key_sentence = self.preprocessing(ks, "key_sentence")
        
        compare_vector = self.get_sentence_vector(key_sentence)
        '''
        braycurtis       -- the Bray-Curtis distance.
        chebyshev        -- the Chebyshev distance.
        correlation      -- the Correlation distance.
        cosine           -- the Cosine distance.
        euclidean        -- the Euclidean distance.
        minkowski        -- the Minkowski distance.
        sqeuclidean      -- the squared Euclidean distance.
        '''
        #these are DISTANCES, similarity is only in the variables <sim>, <best_matches>, and <best_matches_all_methods>
        distances = dict()
        distances["braycurtis"] = scipy.spatial.distance.braycurtis(input_vector,compare_vector)
        distances["chebyshev"] = scipy.spatial.distance.chebyshev(input_vector,compare_vector)
        distances["correlation"] = scipy.spatial.distance.correlation(input_vector,compare_vector)
        distances["cosine"] = scipy.spatial.distance.cosine(input_vector,compare_vector)
        distances["euclidean"] = scipy.spatial.distance.euclidean(input_vector,compare_vector)
        distances["minkowski"] = scipy.spatial.distance.minkowski(input_vector,compare_vector)
        distances["sqeuclidean"] = scipy.spatial.distance.sqeuclidean(input_vector,compare_vector)
        sim = 1.0 - distances[self.method]

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
          self.best_matches_all_methods[function_id]["chebyshev"] = (1.0 - distances["chebyshev"]) * 100
          self.best_matches_all_methods[function_id]["correlation"] = (1.0 - distances["correlation"]) * 100
          self.best_matches_all_methods[function_id]["cosine"] = (1.0 - distances["cosine"]) * 100
          self.best_matches_all_methods[function_id]["euclidean"] = (1.0 - distances["euclidean"]) * 100
          self.best_matches_all_methods[function_id]["minkowski"] = (1.0 - distances["minkowski"]) * 100
          self.best_matches_all_methods[function_id]["sqeuclidean"] = (1.0 - distances["sqeuclidean"]) * 100

    
    top_matches = {key: val for key, val in sorted(self.best_matches.items(), key=lambda item: item[1], reverse=True)}
    top_matches = list(top_matches.items())
    
    #return only top <limit> items
    if len(top_matches) == 0:
      print("ERROR: top_matches empty")
    elif limit == 1:
      top_matches = top_matches[0]
    elif limit > 0 and limit < len(top_matches):
      top_matches = top_matches[:limit]

    return top_matches


  '''
  create comparison of calculation methods. argument <method> defines by which method the ranking is calculated
  all other available methods will be shown in extra columns
  function returns:
    choice: a tuple ("function_id", probability)
    certainty: the difference in probability to the second most probable outcome
    ret_val: list of strings with evenly spaced columns that show the probabilites of all outcomes over all methods to print to console or file
  '''
  def method_comparison(self, input_str, method="cosine", limit=5):
    ret_val = [input_str]
    ranking = self.map_to_eric_function(input_str)
    choice = ranking[0]
    if len(ranking) >= 2:
      certainty = (ranking[0][1] - ranking[1][1]) * 100
    else:
      certainty = -1.0

    first = True
    out_lines = [["function_id", "<CALCULATED>"]]
    for fct_id, similarity in ranking:
      one_line = [fct_id, f"{similarity*100.0}"]
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


  '''
  preprocess message (e.g. remove punctuation, all lower case, ...)
  input_type is one of ["usr_input", "key_sentence"] as some preprocessing is excluded from some types
  
  abbreviations:
    "rsc": remove_stop_chars
    "rnw": remove_non_semantic_words
    "rsw": remove_stop_words
    "rp": remove_pronouns
    "lc": lower_case
    "plh": replace_placeholders
  '''
  def preprocessing(self, strng, input_type):
    preprocessed_string = strng.lstrip().rstrip()
    #print(f"strip: {preprocessed_string}")
    if self.preprocessing_methods["lc"][0]:
      preprocessed_string = preprocessed_string.lower()
    #print(f"lower: {preprocessed_string}")
    if self.preprocessing_methods["rms"][0]:
      preprocessed_string = self.replace_model_specific_phrasings(preprocessed_string)
    #print(f"model_specific: {preprocessed_string}")
    if self.preprocessing_methods["rcp"][0]:
      preprocessed_string = self.replace_critical_phrasings(preprocessed_string)
    #print(f"criticals: {preprocessed_string}")
    if self.preprocessing_methods["rsw"][0]:
      preprocessed_string = self.remove_stop_words(preprocessed_string)
    #print(f"stopwords: {preprocessed_string}")
    if self.preprocessing_methods["rsc"][0]:
      preprocessed_string = self.remove_stop_chars(preprocessed_string)
    #print(f"stopchars: {preprocessed_string}")
    if self.preprocessing_methods["ssc"][0]:
      preprocessed_string = self.space_special_chars(preprocessed_string)
    #print(f"specialchars: {preprocessed_string}")
    if self.preprocessing_methods["rp"][0]:
      preprocessed_string = self.remove_pronouns(preprocessed_string)
    #print(f"pronouns: {preprocessed_string}")
    if self.preprocessing_methods["rnw"][0]:
      preprocessed_string = self.remove_non_semantic_words(preprocessed_string)
    #print(f"non_semantic: {preprocessed_string}")

    if input_type == "usr_input":
      self.extract_placeholders(preprocessed_string)
    elif input_type == "key_sentence":
      if self.preprocessing_methods["plh"][0]:
        preprocessed_string = self.replace_placeholders(preprocessed_string)
    
    return preprocessed_string.lstrip().rstrip()

  def replace_model_specific_phrasings(self, strng):
    ret_val = replace_words(strng, self.model_specific_replacements)
    return ret_val


  def replace_critical_phrasings(self, strng):
    ret_val = replace_words(strng, self.general_replacements)
    return ret_val

  #remove pronouns, so that "I want some hamburgers", "You want some hamburgers", etc. evaluate the same. Testing showed, that removing pronouns is not good though
  def remove_pronouns(self, strng):
    return self.remove_words_from_string(strng, self.pronouns)

  #removing words that have no meaning does not make any difference as those words are not used in the embedding anyway
  def remove_non_semantic_words(self, strng):
    return strng
    #return self.remove_words_from_string(strng, self.non_semantic_words)

  #splits first, then removes, then joins again. This ensures for example that "you" wouldn't match in "your" if you just searched a string for "you"
  def remove_words_from_string(self, strng, words):
    word_list = strng.split()
    ret_val = []
    
    for word in word_list:
      if word.lower() not in words:
        ret_val.append(word)
      
    return " ".join(ret_val)

  #makes the chars (or strings) in self.accepted_special_chars into their own words, e.g. "set age<55" becomes "set age < 55"
  #splits input into words and looks at every word. if a word matches <outcome>, <key> or another reserved word, then it will not space out chars
  #otherwise <outcome> would for example become < outcome > and could not be properly replaced in self.replace_placeholders
  def space_special_chars(self, strng):
    replace_dict = {key: f" {key} " for key in self.accepted_special_chars}
    ret_words = []

    for word in strng.split():
      if word in reserved_placeholder_words:
        ret_words.append(word)
      else:
        ret_words.append(replace_chars(word, replace_dict))

    ret_val = " ".join(ret_words)
    return ret_val

  #remove certain chars that would cause problems or have no use (e.g. punctuation)
  def remove_stop_chars(self, strng):
    ret_val = remove_chars(strng, self.stop_chars)
    return ret_val

  #remove certain words that would otherwise infer with the process but have no real use here (e.g. "please")
  def remove_stop_words(self, strng):
    ret_val = self.remove_words_from_string(strng, self.stop_words)
    return ret_val

  #replace the placeholders of nlp_dictionary["key_sentences"] with actual words that were previously extracted from the user input
  def replace_placeholders(self, strng):
    try:
      key_value_pairs = list(self.placeholders["<key>"].items())
    except:
      print(f"Failed to load placeholders: {self.placeholders}")
      return strng
    ret_val = strng

    '''
    <OUTCOME>
    '''
    if self.placeholders["<outcome>"] is not None:
      outcome = self.placeholders["<outcome>"]
      ret_val = ret_val.replace("<outcome>", outcome, 1)
    '''
    <SUBJECT>
    '''
    if self.placeholders["<subject>"] is not None:
      subject = self.placeholders["<subject>"]
      ret_val = ret_val.replace("<subject>", subject, 1)
    '''
    <KEY> and <VALUE>
    '''
    if self.placeholders["<key>"]:
      #go through string and replace keys and values. always replace only one occurence and increase index
      max_index = len(key_value_pairs)
      key_index = 0
      value_index = 0
      tmp_string = ret_val
      for word in tmp_string.split():
        if word == "<key>" and key_index < max_index:
          replacement = key_value_pairs[key_index][0]
          #if corresponding value is None, skip value
          if key_value_pairs[key_index][1] is None:
            value_index += 1
          key_index += 1
          #print(f"replacing <key> with {replacement}")
          ret_val = ret_val.replace("<key>", replacement, 1)
        elif word == "<value>" and value_index < max_index:
          replacement = key_value_pairs[value_index][1]
          value_index += 1
          #print(f"replacing <value> with {replacement}")
          if replacement:
            ret_val = ret_val.replace("<value>", replacement, 1)
      #if to every key there wasn't always a value to be replaced, return the original sentence.
      #that occures for example with "what if age was greater/lesser" and we shouldn't give that key_sentence
      #an extra word (here "age") to match with the input
      if key_index != value_index:
        #print(f"different indices: returning '{tmp_string}' instead of '{ret_val}'")
        ret_val = strng

    return ret_val

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

  '''
  go through string word by and see if you can find replacements for placeholders
  return None but saves everything in object's attribute self.placeholders
    key: placeholders as they occur in dictionary.nlp_dictionary. as of now these are <key>, <outcome>
    value:  if key==<outcome>: one of the values of server.d["class"]["values"]
            if key==<key>: another dict with 
              key: column name (of model) that was found in input
              value: value for that column name if found in input
  '''
  def extract_placeholders(self, strng):
    self.placeholders = {"<key>": dict(), "<outcome>": None, "<subject>": None}
    words = strng.split()
    used_words = [] #list of indexes of used words
    '''
    <SUBJECT>
    '''
    for subject in self.subject_phrasings:
      if strng.find(subject) > -1:
        self.placeholders["<subject>"] = subject
        break
    '''
    <OUTCOME> and <KEY>/<VALUE>
    '''
    for word, index in zip(words, range(len(words))):
      #if word is a value the outcome can take, save it as <outcome>, elif look if it matches a column name, else it might be a differently phrased <outcome>
      if word in self.model_columns["class"]["values"].values():
        self.placeholders["<outcome>"] = word
        used_words.append(index)
      elif word != "class" and word.capitalize() in self.model_columns.keys():
        value, value_index = self.extract_value(word.capitalize(), words[index+1:])
        self.placeholders["<key>"][word] = value
        used_words.append(value_index+index+1)
      else:
        for v in self.model_columns["class"]["phrasings"].values():
          if word in v:
            self.placeholders["<outcome>"] = word
            used_words.append(index)
            break

    #if no model column was found, go through all of them (if allowed)
    if self.search_for_placeholder_values:
      for model_column in self.model_columns.keys():
        #if a value for that key was not yet found above
        if model_column != "class" and model_column.lower() not in self.placeholders["<key>"].keys():
          value, value_index = self.extract_value(model_column, words)
          if value:
            if value_index not in used_words:
              self.placeholders["<key>"][model_column.lower()] = value
              used_words.append(value_index)

    #print(f"extracted placeholders: {self.placeholders}       {strng}    {used_words}")

  #only called from extract_placeholders. takes rest of sentence as list of words
  #returns first occurence of a fitting value. None if none was found
  def extract_value(self, key, word_list):
    #categorical values
    if self.model_columns[key]["feature-type"] == "categorical":
      possible_values = [x.lower() for x in self.model_columns[key]["values"].values()]
      for w, index in zip(word_list, range(len(word_list))):
        if w in possible_values:
          return w, index
    #continuous values
    elif self.model_columns[key]["feature-type"] == "continuous":
      #min = self.model_columns[key]["values"]["min"]
      #max = self.model_columns[key]["values"]["max"]
      for w, index in zip(word_list, range(len(word_list))):
        try:
          #as_number = float(w)
          float(w)
          # if as_number >= min and as_number <= max:
          return w, index
        except ValueError:
          pass
    return None, -1


  #return vector representation of sentence (for now only fasttext is used)
  def get_sentence_vector(self, msg):
    return self.ft.get_sentence_vector(msg)

  #takes message and returns the id of the top <limit> functions in dictionary.dictionary that are most similiar to the message
  #return value is a dictionary with fct_id as key and float as value
  def get_similarity_ranking(self, input_message, method="cosine", limit=2):
    input_vector = self.get_sentence_vector(input_message)
    if self.normalise_embedding:
      input_vector = normalise_vector(input_vector)


    #go through all eric-functions and their key_sentences
    self.best_matches = dict()
    self.best_matches_all_methods = dict()
    for function_id, list_of_key_sentences in self.key_sentences.items():
      for ks in list_of_key_sentences:
        #tmp_stop_chars = [x for x in self.stop_chars if x not in ["<", ">"]]
        #asdf = remove_chars(key_sentence, tmp_stop_chars).lower()
        key_sentence = self.preprocessing(ks, "key_sentence")
        if ks.find("<subject>") > -1:
          print(f"keysent: {ks}")
          print(f"prepped: {key_sentence}")

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
          # print(f"         better: ({function_id}) ({sim}) {key_sentence}")
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
def remove_chars(strng, chars_to_remove):
  removal_dict = {key: " " for key in chars_to_remove}
  return replace_chars(strng, removal_dict)

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

def replace_words(sentence, replacements):
  ret_val = sentence
  for finder, replacement in replacements.items():
    ret_val = ret_val.replace(finder, replacement)
  return ret_val

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

def test_sentences_from_console(eric):
  print("Please provide input:")
  while True:
    usr_in = input()
    if usr_in.lower() in ["exit", "exit()", "quit", "quit()", "end", "end()"]:
      break
    else:
      result = eric.map_to_eric_function(usr_in)
      print(f"result: {result}")


if __name__ == "__main__":
  model, method = "wiki.en.bin", "minkowski"
  eric = Eric_nlp()
  eric.method = method
  eric.load_model(f"data\\{model}")
  eric.stanza_pipeline = depparse.init_stanza("en")

  test_sentences_from_console(eric)