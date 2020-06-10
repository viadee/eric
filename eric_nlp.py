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
          "died": ["die", "dies", "dead", "passed away", "perish", "perished", "dying"],
          "survived": ["survive", "survives", "live", "lives", "alive", "living"]
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
    self.valid_answers = "" #example: 
    self.usr_input_traceback = ["User input:"] #store every received message here to trace back and reproduce if an error occurs
    self.normalise_embedding = False
    self.model_columns = d
    self.best_matches = dict()
    self.best_matches_all_methods = dict()
    self.placeholders = dict()#example: {'<key>': {'Age': '23', 'Sex': 'Male'}, '<outcome>': 'died'}
    self.placeholder_duplicates = [] #saves duplicate entries, e.g. if user writes "what if age is 22 and age is 11": age 22 will be stored in placeholders, age 11 in placeholder_duplicates
    self.search_for_placeholder_values = True #if true, extract_placeholders() will look for model values even if no model name was found in the input
    self.bad_input = True
    self.prioritise_negation = True #if two depparse templates match some input, the negated one is preferred
    self.init_key_sentences()#key: function-id, value: list of strings
    self.accepted_special_chars = ["=", "<", ">", "-"]
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
      "n't you": " you not",
      "n't": " not",
      "’": "'"
    }
    self.model_specific_replacements = {
      "first class": "first pclass",
      "second class": "second pclass",
      "third class": "third pclass",
      " class": " pclass", #if there is no space, "pclass" from input will become "ppclass"
      "1st": "first",
      "2nd": "second",
      "3rd": "third"
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
      "plh": (True, "Replace placeholders in key sentences"),
      "rmi": (True, "Remove multiple inputs"), #removes all but one input pair if user provides multiple (but they get saved in self.placeholders). example: "what if age was 22, relatives 3, pclass first" => "what if age was 22" 
      "cln": (True, "Reduce decimal points") # reduces too many decimal points. e.g. 'what if age was -44,4.4.5..6?' becomes 'what if age was -44.4456?'
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
      if re.match(f"^{self.valid_answers['value']}$", message):
        print(f"matched '{message}' to '{self.valid_answers['value']}'")
        return message, True
    elif self.valid_answers["type"] == "selection":
      for va in self.valid_answers["value"]:
        if message.lower() == va.lower():
          print(f"matched '{message}' to '{va}'")
          return va, True
    else:
      print(f"ERROR: unknown answer type: {self.valid_answers}")
  
    print(f"could not match '{message}' to '{self.valid_answers}'")
    return message, False

  #does not do preprocessing
  def get_function_match(self, sentence):
    if not self.ft:
      print("ERROR: No model loaded for eric_nlp object")
      return
    if not self.stanza_pipeline:
      self.stanza_pipeline = depparse.init_stanza(self.language)
    
    #tuple (fct_id, similarity in percent)
    similarity_result = self.get_similarity_result(sentence)
    similarity_result_similarity = similarity_result[1][0]
    similarity_result_matched_sentence = similarity_result[1][1]
    similarity_result_matched_sentence_preprocessed = similarity_result[1][2]
    print(f"      THRESHOLDS: {self.depparse_threshold} :: {self.deny_threshold}")
    print(f" PASSED SENTENCE: '{sentence}'")
    print(f"SIMILARITY CHOSE: {similarity_result}")

    result = similarity_result[0]
    if similarity_result_similarity < self.depparse_threshold:
      tree = self.stanza_pipeline(sentence).sentences[0]
      depparse_ranking = depparse.get_matching_dictionary_trees(tree, self)
      try:
        if len(depparse_ranking) == 0:
          depparse_result = ("none", [])
        else:
          #tuple (fct_id, matching tree template)
          depparse_result = (depparse_ranking[0][0], depparse_ranking[0][1])
          result = depparse_result[0]
        print(f"  DEPPARSE CHOSE: {depparse_result}")
      except:
        print("could not work with depparse ranking:")
        print(depparse_ranking)
        quit()
    else:
      print(f"only SIMILARITY: {similarity_result[0]} :: {similarity_result_similarity}")
      depparse_result = ("none", [f"No depparsing necessary; similarity >= depparse_threshold ({similarity_result_similarity} >= {self.depparse_threshold})"])

    if depparse_result[0] == "none" and similarity_result_similarity < self.deny_threshold:
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
            if self.best_matches[function_id][0] < sim:
                self.best_matches[function_id] = (sim, ks, key_sentence)
                update_methods = True
        else:
            self.best_matches[function_id] = (sim, ks, key_sentence)
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

    
    top_matches = {key: val for key, val in sorted(self.best_matches.items(), key=lambda item: item[1][0], reverse=True)}
    top_matches = list(top_matches.items())

    
    #return only top <limit> items
    if len(top_matches) == 0:
      print("ERROR: top_matches empty")
    elif limit == 1:
      top_matches = top_matches[0]
    elif limit > 0 and limit < len(top_matches):
      top_matches = top_matches[:limit]
    
    print(f"TOP MATCHES: {top_matches}")
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
    # print(f"strip: {preprocessed_string}")
    if self.preprocessing_methods["lc"][0]:
      preprocessed_string = preprocessed_string.lower()
    # print(f"lower: {preprocessed_string}")
    if self.preprocessing_methods["rms"][0]:
      preprocessed_string = self.replace_model_specific_phrasings(preprocessed_string)
    # print(f"model_specific: {preprocessed_string}")
    if self.preprocessing_methods["rcp"][0]:
      preprocessed_string = self.replace_critical_phrasings(preprocessed_string)
    # print(f"criticals: {preprocessed_string}")
    if self.preprocessing_methods["rsw"][0]:
      preprocessed_string = self.remove_stop_words(preprocessed_string)
    # print(f"stopwords: {preprocessed_string}")
    if self.preprocessing_methods["rsc"][0]:
      preprocessed_string = self.remove_stop_chars(preprocessed_string)
    # print(f"stopchars: {preprocessed_string}")
    if self.preprocessing_methods["ssc"][0]:
      preprocessed_string = self.space_special_chars(preprocessed_string)
    # print(f"specialchars: {preprocessed_string}")
    if self.preprocessing_methods["rp"][0]:
      preprocessed_string = self.remove_pronouns(preprocessed_string)
    # print(f"pronouns: {preprocessed_string}")
    if self.preprocessing_methods["rnw"][0]:
      preprocessed_string = self.remove_non_semantic_words(preprocessed_string)
    # print(f"non_semantic: {preprocessed_string}")

    if input_type == "usr_input":
      if self.preprocessing_methods["cln"][0]:
        preprocessed_string = self.clean_numbers(preprocessed_string)
      self.extract_placeholders(preprocessed_string)
      print(f"extracted placeholders: {self.placeholders}")
      print(f"  extracted duplicates: {self.placeholder_duplicates}")
      if self.preprocessing_methods["rmi"][0]:
        preprocessed_string = self.remove_multiple_inputs(preprocessed_string)
        # print(f"remove_multiple_inputs: {preprocessed_string}")
    elif input_type == "key_sentence":
      if self.preprocessing_methods["plh"][0]:
        preprocessed_string = self.replace_placeholders(preprocessed_string)

    
    
    return preprocessed_string.lstrip().rstrip()

  def backwards_replace(self, strng, old, new, count=1):
    #print(f"looking for {old} in {strng}")
    ret_val = strng.rsplit(old, count)
    return new.join(ret_val)

  def remove_multiple_inputs(self, strng):
    #print(f"removing: {self.placeholders}")
    #print(f"     and: {self.placeholder_duplicates}")
    ret_val = strng.split()
    first = True
    #skip the first, to keep one
    for k, v in self.placeholders["<key>"].items():
      if first:
        first = False
      else:
        #print(f"removing '{k.lower()}' and '{v.lower()}' from {ret_val}")
        if k.lower() in ret_val:
          ret_val.remove(k.lower())
        if v:#could be None
          if v.lower() in ret_val:
            ret_val.remove(v.lower())

    ret_val = " ".join(ret_val)

    for duplicate in self.placeholder_duplicates:
      #print(f"D_removing '{duplicate.lower()}' from '{ret_val}'")
      ret_val = self.backwards_replace(ret_val, duplicate.lower(), "")

    #if you remove inputs, you have to remove trailing "and"s
    ret_val = self.remove_trailings(ret_val, "and")
    
    return ret_val

  def remove_trailings(self, sentence, word, case_sensitive=False):
    words = []
    trail = True #becomes false when first trailing word not equal to <word> is found
    reversed = sentence.split()
    reversed.reverse()
    for w in reversed:
      if case_sensitive:
        if w == word:
          if not trail:
            words.append(w)
        else:
          words.append(w)
          trail = False
      else:
        if w.lower() == word.lower():
          if not trail:
            words.append(w)
        else:
          words.append(w)
          trail = False

    words.reverse()
    return " ".join(words)



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


  '''
  expands clips message with parameters from self.placeholders if suitable. example: "whatif" -> "whatif Age 22 Embarked Cherbourg"
  returns message unmodified if no suitable parameters were found
  
  functions that use parameters:
    outcome parameters:
      when
      how-to
      why-not
    key parameters:
      whatif-gl
    key-value parameters:
      whatif
  '''
  def expand_with_parameters(self, message):
    need_outcome = ["when", "how-to", "why-not"]
    need_key = ["whatif-gl"]
    need_key_value = ["whatif"]
    ret_val = message
    # OUTCOME
    if message in need_outcome:
      if self.placeholders["<outcome>"]:
        o = self.placeholders["<outcome>"]
        if o not in self.model_columns["class"]["values"].values():
          for k, v in self.model_columns["class"]["phrasings"].items():
            if o in v:
              o = k
              break        
        #print(f" expanding with ' {o}'")
        ret_val += f" {o}"

    # KEY ---- this adds multiple keys if more than one entry is present
    elif message in need_key:
      for k in self.placeholders["<key>"].keys():
        if k:
          #print(f" expanding with ' {k}'")
          ret_val += f" {k}"

    # KEY-VALUE-PAIRS
    elif message in need_key_value:
      for k, v in self.placeholders["<key>"].items():
        if v:#can be None
          v_prepared = self.make_int(v) if self.model_columns[k]["data-type"] == "integer" else v
          expand = f" {k} {v_prepared}"
          #print(f" expanding with '{expand}'")
          ret_val = f"{ret_val}{expand}"

    return ret_val

  
  #remove certain chars that would cause problems or have no use (e.g. punctuation)
  def remove_stop_chars(self, strng):
    #handle decimal comma/point separately
    puncts = [",", "."]
    stopper = [x for x in self.stop_chars if x not in puncts]
    pre_ret_val = remove_chars(strng, stopper)

    ret_val = ""
    for i, prv in enumerate(pre_ret_val):
      if prv in puncts:
        next_char = pre_ret_val[i+1] if i+1 < len(pre_ret_val) else ""
        prev_char = pre_ret_val[i-1] if i > 0 else ""
        #in case of two adjacent puncts: replace the first with a 1 but do not copy anything to ret_val.
        #that way, the last of multiple adjacent puncts can be safely copied if it is followed by a number.
        #and by replacing a punct with "1" you ensure the integrity of the indexes
        if next_char in puncts:
          tmp = list(pre_ret_val)
          tmp[i] = "1"
          pre_ret_val = "".join(tmp)
        elif next_char.isdigit() and prev_char.isdigit():
          ret_val += prv
        else:
          ret_val += " "
      else:
        ret_val += prv

    # print(f"ORIGINAL: '{strng}'")
    # print(f" CLEANED: '{ret_val}'")
    return ret_val

  def make_int(self, value_as_str):
    if not value_as_str:#if None
      return ""
    delimiters = [",", "."]
    ret_val = value_as_str
    for deli in delimiters:
      index = ret_val.find(deli)
      if index > 0:
        ret_val = ret_val[:index]
      elif index == 0:
        ret_val = "0"
      
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

    if self.preprocessing_methods["lc"][0]:
      return ret_val.lower()
    else:
      return ret_val

 
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
    self.placeholder_duplicates = []
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
        #if not value:
          #print(f"WARNING: could not find value for '{word}' in: {strng}")
        if word.capitalize() in self.placeholders["<key>"].keys():
          self.placeholder_duplicates.append(word.capitalize())
          if value:
            self.placeholder_duplicates.append(value)
        else:
          self.placeholders["<key>"][word.capitalize()] = value
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
              self.placeholders["<key>"][model_column] = value
              used_words.append(value_index)

    #print(f"extracted placeholders: {self.placeholders}       {strng}    {used_words}")

  #only called from extract_placeholders. takes rest of sentence as list of words
  #returns first occurence of a fitting value. None if none was found
  def extract_value(self, key, word_list):
    #categorical values
    if self.model_columns[key]["feature-type"] == "categorical":
      possible_values = [x for x in self.model_columns[key]["values"].values()]
      for w, index in zip(word_list, range(len(word_list))):
        for pv in possible_values:
          if w == pv.lower():
            return pv, index
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

  #takes a sentence as string and cleans decimal points for every word. e.g. words like "3,5.21,6,8" become "3.52168" or ".33" becomes "0.33"
  def clean_numbers(self, strng):
    ret_val = []
    for w in strng.split():
      word = self.reduce_decimal_points(w)
      ret_val.append(word)
    
    ret_val = " ".join(ret_val)
    print(f"REDUCED DECIMAL: '{strng}' -> '{ret_val}'")
    return ret_val


  #takes one word of a sentence as a string
  #changes all "," to ".", then strips all but the first of those, so a float with only one decimal point (or an integer if no , or . was present) is yielded
  #digits between the redundant "." become decimal places
  #returns the clean float or integer as string or the word as it was passed to the function if string wasn't a number
  def reduce_decimal_points(self, word):
    word_modified = word.replace(",", ".")
    ret_val = ""
    first = True
    for w in word_modified:
      if w == ".":
        if first:
          ret_val += w
          first = False
      else:
        ret_val += w

    if ret_val:
      if ret_val[0] == ".":
        ret_val = f"0{ret_val}"
      elif ret_val[-1] == ".":
        ret_val = ret_val[:-1]
    else:
      ret_val = word

    return ret_val

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
          print(f"replace <subject>: '{ks}' :::::  '{key_sentence}'")

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