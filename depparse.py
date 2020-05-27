import pickle
import stanza
import test_stuff
from datetime import datetime
from dictionary import cd, dictionary
import eric_nlp


#does not do preprocessing
def depparse(sentences, pipeline):
    output = ["OUTPUT:\n"]
    roots = dict()
    for sentence in sentences:
        doc = pipeline(sentence)

        #get max_width for pretty printing
        max_width_word = 0
        for word in sentence.split():
            width = len(word)
            if width > max_width_word:
                max_width_word = width

        append_data = []
        for sent in doc.sentences:
            sentence_words = ""
            root = ""
            
            max_width_deprel = 0
            for word in sent.words:
                if len(word.deprel) > max_width_deprel:
                    max_width_deprel = len(word.deprel)

            for word in sent.words:
                if word.head == 0:
                    root = word.text
                append_data.append(f'id: {word.id}\tword: {word.text.ljust(max_width_word)}\tlemma: {word.lemma.ljust(max_width_word)}\tupos: {word.upos}\txpos: {word.xpos.ljust(3)}\thead id: {word.head}\thead: {sent.words[word.head-1].text.ljust(max_width_word) if word.head > 0 else "root".ljust(max_width_word)}\tdeprel: {word.deprel.ljust(max_width_deprel)}\tfeats: {word.feats}')
                sentence_words += f"{word.text} "
            
            #console and/or txt-file output
            append_data.append("="*47 + "\n")
            output.append(sentence_words)
            output.append(f"Root: {root}")
            output.extend(append_data)
            if root.lower() in roots.keys():
                roots[root.lower()] += 1
            else:
                roots[root.lower()] = 1

    roots = {key: val for key, val in sorted(roots.items(), key=lambda item: item[1], reverse=True)}
    return output, roots


def init_stanza(lang):
    print(f"loading pipeline for language '{lang}'")
    #with open("data\\pipeline.pickle", "rb") as f:
    #    stanza_pipeline = pickle.load(f)
    stanza.download(lang)
    stanza_pipeline = stanza.Pipeline(lang=lang, processors="tokenize,mwt,pos,lemma,depparse")
    print("successfully loaded pipeline")
    return stanza_pipeline

'''
creates a matrix with:
    columns: roots
    rows: count how often that root occurs for a function
'''
def create_roots_matrix(roots, file_name, csv_sep = ";", empty_cell = "0"):
    file_lines = []
    first_line = f"{empty_cell}"
    first = True
    for root, functions in roots.items():
        line = f"{root}"
        tmp = [x["id"] for x in dictionary]
        tmp.append("none")
        for fct_id in tmp:
            if first:
                first_line += f"{csv_sep}{fct_id}"
            
            if fct_id in functions.keys():
                count = functions[fct_id]
            else:
                count = empty_cell
            line += f"{csv_sep}{count}"
        if first:
            file_lines.append(first_line)
            first = False
        file_lines.append(line)


    test_stuff.list_to_file(file_lines, file_name)

#all_roots is a dict from words to another dict from function ids to ints
#roots is expected to be a dict from words to ints
def extend_roots(all_roots, roots, fct_id):
    for k, v in roots.items():
        if k in all_roots.keys():
            if fct_id in all_roots[k].keys():
                print(f"DUPLICATE FUNCTION IN ROOTS: {fct_id} ; {k} ; {v}")
            else:
                all_roots[k][fct_id] = v
        else:
            print(f"adding new word: {k} from {fct_id} ;; {v}")
            all_roots[k] = {fct_id: v}
    return all_roots

#attempt 1: how many nodes do they share, regardless of node depth
def tree_compare_bad(tree1, tree2):
    if len(tree1.words) < len(tree2.words):
        small = tree1
        big = tree2
    else:
        small = tree2
        big = tree1
    
    
    in_common = 0
    used_ids = []
    for leaf_s in small.words:
        found_leaf_id = ""
        for leaf_b in big.words:
            if leaf_s.deprel == leaf_b.deprel and leaf_b.id not in used_ids:
                found_leaf_id = leaf_b.id
                break
        if found_leaf_id:
            in_common += 1
            used_ids.append(found_leaf_id)

    percentage = in_common * 100.0 / len(small.words)

    return in_common, percentage

def tree_compare_bad_again(tree1, tree2):
    bad_id = "0"
    if len(tree1.words) < len(tree2.words):
        small = tree1
        big = tree2
    else:
        small = tree2
        big = tree1

    similar_counter = 0
    used_ids = []
    for word_b in big.words:
        found_id = bad_id
        #head_b = big.words[int(word_b.head)-1] if word_b.head != 0 else "root"
        for word_s in small.words:
            #head_s = small.words[int(word_s.head)-1] if word_s.head != 0 else "root"

            if word_b.lemma == word_s.lemma and word_b.deprel == word_s.deprel and word_b.head == word_s.head:
                if word_s.id not in used_ids:
                    found_id = word_s.id
        if found_id != bad_id:
            similar_counter += 1
            used_ids.append(found_id)

    percentage = similar_counter * 100.0 / len(small.words)
    return similar_counter, percentage

#a tree is a list of dictionarys. every dictionary represents a word of the sentence. key-value-pairs are the attributes of that word.
def tree_compare(t1, t2):
    return tree_compare_bad_again(t1, t2)

def get_word(wanted_id, words):
    if wanted_id == "0":
        return "root"
    for word in words:
        if word.id == wanted_id:
            return word
    return ""

'''
takes a tuple as in "deprel" in dictionary.dictionary.
returns list of tuples. if master_tuple was a simple tuple, the list only contains that tuple
if master_tuple has lists as elements, these get split so that every tuple in the returned list has only strings as elements
Example:
    in: (["predict", "divinate"], "obl", ["data", "person"])
    out: [
        ("predict", "obl", "data"),
        ("predict", "obl", "person"),
        ("divinate", "obl", "data"),
        ("divinate", "obl", "person")
    ]
note: returning list has x elements with x being the product of all three lengths. (here 2*1*2 = 4)
'''
def generate_sub_tuples(master_tuple):
    ret_val = []
    element_0 = master_tuple[0] if isinstance(master_tuple[0], list) else [master_tuple[0]]
    element_1 = master_tuple[1] if isinstance(master_tuple[1], list) else [master_tuple[1]]
    element_2 = master_tuple[2] if isinstance(master_tuple[2], list) else [master_tuple[2]]

    for e_0 in element_0:
        for e_1 in element_1:
            for e_2 in element_2:
                tpl = (e_0, e_1, e_2)
                ret_val.append(tpl)
    return ret_val


'''
takes a word-object of a depparse-word and a string element from a tuple (not a list-element. use generate_sub_tuples() first)
checks if dictionary.category_tag (by default "#") is in tuple_element. If so, it extracts which attribute (i.e. in front of "#") is wanted.
then returns the corresponding attribute value of word_object and the part right of "#" in tuple_element
if "#" was not in tuple_element, it returns tuple_element as it is and the default attribute of word_object
also needs an eric, to invoke replacement of placeholders
'''
def get_comparison_attributes(word_object, tuple_element, eric, default="text"):
    debug_on = False
    greatless = True if tuple_element in [f"lemma{cd}<", f"lemma{cd}>"] else False
    #if word_object is a root_word, it will be a dictionary, as root words don't exist and are constructed synthetically in the function get_mother()
    if isinstance(word_object, dict):
        if cd in tuple_element:
            splitted = tuple_element.split(cd)
            ret_word_attribute = word_object[splitted[0]]
            ret_tuple_attribute = splitted[1]
        else:
            ret_word_attribute = word_object[default]
            ret_tuple_attribute = tuple_element
        '''DEBUG-BEGIN'''
        if debug_on:
            import datetime
            f = "output\\depparse\\splitter_test.txt"
            headline = "/"*30
            ts = "JETZT"##datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            out = [
                f"{headline}",
                f"{ts}",
                f"{headline}",
                f"tuple_element: {tuple_element}",
                f"word_object:",
                f"\t      id: {word_object['id']}",
                f"\t    text: {word_object['text']}",
                f"\t   lemma: {word_object['lemma']}",
                f"\t    upos: {word_object['upos']}",
                f"\t    xpos: {word_object['xpos']}",
                f"\t head_id: {word_object['head']}",
                f"\t  deprel: {word_object['deprel']}",
                f" ret_word_attribute: {ret_word_attribute}",
                f"ret_tuple_attribute: {ret_tuple_attribute}"
                f"\n"
            ]
            test_stuff.list_to_file(out, f, mode="a")
        '''DEBUG-END'''
    else:
        if cd in tuple_element:
            splitted = tuple_element.split(cd)
            ret_word_attribute = getattr(word_object, splitted[0])
            ret_tuple_attribute = splitted[1]
        else:
            ret_word_attribute = getattr(word_object, default)
            ret_tuple_attribute = tuple_element
        
        '''DEBUG-BEGIN'''
        if debug_on:
            import datetime
            f = "output\\depparse\\splitter_test.txt"
            headline = "/"*30
            ts = "JETZT"#datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            out = [
                f"{headline}",
                f"{ts}",
                f"{headline}",
                f"tuple_element: {tuple_element}",
                f"word_object:",
                f"\t      id: {word_object.id}",
                f"\t    text: {word_object.text}",
                f"\t   lemma: {word_object.lemma}",
                f"\t    upos: {word_object.upos}",
                f"\t    xpos: {word_object.xpos}",
                f"\t head_id: {word_object.head}",
                f"\t  deprel: {word_object.deprel}",
                f" ret_word_attribute: {ret_word_attribute}",
                f"ret_tuple_attribute: {ret_tuple_attribute}"
                f"\n"
            ]
            test_stuff.list_to_file(out, f, mode="a")
        '''DEBUG-END'''
    ret1, ret2 = replace_depparse_placeholders(ret_word_attribute, ret_tuple_attribute, eric)
    if debug_on and greatless:
        print(f"{word_object} ::: '{ret1}' /// {tuple_element} ::: '{ret2}'")
    return ret1, ret2

'''
word_attribute should be from the user input, tuple_attribute one element of a tuple from the depparse templates in dictionary.
it's called attribute, not element because it should only be called at the end of get_comparison_attributes() which extracts attributes from word objects (e.g. the lemma, upos or deprel, etc.)
word_attribute needs to be included even though it will not have any placeholders. In the case, that "<outcome>" is in tuple_attribute, word_attribute needs to be checked
if it is a different form of the possible outcomes. This gets checked via the eric.model_columns["class"]["phrasings"] dict which has all possible outcomes as keys (here "survived" and "died")
and stores different forms of those as the values of that dict as list. Here ["survive", "survives"] and ["die", "dies"].
'''
def replace_depparse_placeholders(word_attribute, tuple_attribute, eric):
    ret_word_attribute, ret_tuple_attribute = word_attribute, tuple_attribute
    
    if ret_tuple_attribute == "<outcome>":
        if eric.placeholders["<outcome>"]:
            ret_tuple_attribute = eric.placeholders["<outcome>"]
    
    elif ret_tuple_attribute == "<key>":
        if ret_word_attribute in eric.placeholders["<key>"].keys():
            ret_tuple_attribute = ret_word_attribute    
    elif ret_tuple_attribute == "<value>":
        if ret_word_attribute in eric.placeholders["<key>"].values():
            ret_tuple_attribute = ret_word_attribute

    test_stuff.logger(f"DEPREPLACE: {word_attribute} // {ret_word_attribute} ::::: {tuple_attribute} // {ret_tuple_attribute} ::::: {eric.placeholders}")
    return ret_word_attribute, ret_tuple_attribute

#looks for the head/mother node of word in tree and returns it (or a representing dictionary if head is root).
#returns dict since root is not really represented in the word objects of depparse
def get_mother(word, tree):
    if word.head == 0:
        return {
            "id": "0",
            "text": "root",
            "lemma": "root",
            "upos": None,
            "xpos": None,
            "head": None,
            "deprel": None
        }
    else:
        return tree.words[word.head-1]



#takes a depparse tree t and goes through the depparse tree templates in dictionary.dictionary.
#returns a list of tuples (fct_id, tree template) with a tuple for every found match.
def get_matching_dictionary_trees(tree, eric):
    tab = "\t"
    mother_index = 0
    deprel_index = 1
    child_index = 2
    all_matches = []
    for d in dictionary:
        test_stuff.logger(f"/////: {d['id'].upper()} ://///")
        for depparse_template in d["depparse"]:
            test_stuff.logger(f"{tab*1}template: {depparse_template}")
            used_words = [] #already matched words. saved to not use them twice
            template_match = True #stays true unless at least one tuple in the demplate does not match
            match_sub_tuples = [] #stores the sub_tuples that matched in this template. So when a total match is achieved, the used subtuples can be viewed
            #if a depparse template is an empty list, it would always match, so skip it. this should never happen, if dictionary was created properly, but just to be safe
            if len(depparse_template) == 0:
                continue
            for template_tuple in depparse_template:
                test_stuff.logger(f"{tab*2}tuple: {template_tuple}")
                tuple_correct = False
                sub_tuples = generate_sub_tuples(template_tuple)
                for sub_tuple in sub_tuples:
                    test_stuff.logger(f"{tab*3}sub_tuple: {sub_tuple[mother_index]}, {sub_tuple[deprel_index]}, {sub_tuple[child_index]}")
                    sub_tuple_correct = False
                    for word in tree.words:
                        if word.id in used_words:
                            test_stuff.logger(f"{tab*4}{word.text.upper()}: >>>skipped<<<")
                            continue
                        
                        test_stuff.logger(f"{tab*4}{word.text.upper()}: id: {word.id} :: text: {word.text} :: lemma: {word.lemma} :: upos: {word.upos} :: xpos: {word.xpos} :: feats: {word.feats} :: head: {word.head} :: deprel: {word.deprel} :: misc: {word.misc}")
                        
                        #the following get generated over function to use different attributes of the words (see function for more info)
                        child_val, tuple_child_val = get_comparison_attributes(word, sub_tuple[child_index], eric)
                        deprel_val, tuple_deprel_val = get_comparison_attributes(word, sub_tuple[deprel_index], eric, default="deprel")
                        test_stuff.logger(f"{tab*5}vals: {child_val},{tuple_child_val}, {deprel_val}, {tuple_deprel_val}")

                        child_matched = True if child_val.lower() == tuple_child_val.lower() else False
                        deprel_matched = True if deprel_val.lower() == tuple_deprel_val.lower() else False

                        #just to not look up the mother if the match already failed
                        if child_matched and deprel_matched:
                            mother = get_mother(word, tree)
                            mother_val, tuple_mother_val = get_comparison_attributes(mother, sub_tuple[mother_index], eric)
                            mother_matched = True if mother_val.lower() == tuple_mother_val.lower() else False
                        else:
                            mother_matched = False
                        
                        #if all three categories are a match, the subtuple is a match
                        if child_matched and deprel_matched and mother_matched:
                            used_words.append(word.id)
                            sub_tuple_correct = True
                            break #no need to match the other words. match next tuple instead

                    #if one of the sub_tuples is correct it's a match for the whole tuple, so no need to match the others
                    if sub_tuple_correct:
                        match_sub_tuples.append(sub_tuple)
                        tuple_correct = True
                        break
                #if one tuple in a template does not match, the whole template does not match, so no need to go on
                if not tuple_correct:
                    template_match = False
                    break
            #collect all template matches
            if template_match:
                tmp = (d["id"], match_sub_tuples)
                all_matches.append(tmp)

    #returns a list of tuples with two elements each: 1st fct_id, 2nd the tree template that matched, i.e. a list of tuples
    #largest template tree will be element 0
    
    #print("/"*30)
    #print(f"before: {all_matches}")
    if eric.prioritise_negation:
        ret_val = prioritise_negation(all_matches)
    else:
        ret_val = sorted(all_matches, key=lambda item: len(item[1]), reverse=True)

    
    #print(f"after: {ret_val}")
    #print("/"*30)
    return ret_val

#expects a list of tuples with two elements each: 1st fct_id, 2nd the tree template that matched, i.e. a list of tuples
#that list should represend a ranking from most likely (lowest index) to least likey (highest index)
#it then goes through all templates and sorts them into templates that contain a lemma:not and and those that do not
#then creates a ranking again for both, separately
#then, both lists get concatenated with the negated tuples at the lower indices. So a short but negated template will have priority over a longer, non-negated one
#returns that list
def prioritise_negation(templates_list):
    negated_tuples = []
    non_negated_tuples = []
    for template in templates_list:
        negated = False

        for tpl in template[1]:
            head = tpl[0]
            child = tpl[2]
            if isinstance(head, list):
                if f"lemma{cd}not" in head or "not" in head:
                    negated = True
                    break
            else:
                if f"lemma{cd}not" == head or "not" == head:
                    negated = True
                    break
            if isinstance(child, list):
                if f"lemma{cd}not" in child or "not" in child:
                    negated = True
                    break
            else:
                if f"lemma{cd}not" == child or "not" == child:
                    negated = True
                    break

        if negated:
            negated_tuples.append(template)
        else:
            non_negated_tuples.append(template)

    negated_tuples = sorted(negated_tuples, key=lambda item: len(item[1]), reverse=True)
    non_negated_tuples = sorted(non_negated_tuples, key=lambda item: len(item[1]), reverse=True)
    ranked_list = negated_tuples + non_negated_tuples

    return ranked_list





#t is a tree like in tree_compare(t1, t2)
def dictionary_templates_test(tree):
    #indices of tuples in templates
    tmother = 0 #mother node
    tdeprel = 1 #dependency relation
    tchild = 2 #child node

    root = ""
    for x in tree.words:
        if x.head == 0:
            root = x
            break
    if not root:
        test_stuff.logger("no root found:")
        test_stuff.logger(tree.words)

    test_stuff.logger("Testing Tree:")
    for d in dictionary:
        test_stuff.logger(f"MATCHING TO {d['id']}")
        if "depparse" not in d.keys():
            continue
        template_counter = 0
        for dep_template in d["depparse"]:
            template_counter += 1
            correct_tupel_counter = 0 #if correct match, correct_tupel_counter should be equal to the number of elements in dep_template
            test_stuff.logger(f"\t\t template {template_counter}")
            for tup in dep_template:
                found_mother = False
                found_child = False
                found_deprel = False
                test_stuff.logger(f"\t\t\t{tup}")
                child_is_list = True if isinstance(tup[tchild], list) else False
                deprel_is_list = True if isinstance(tup[tdeprel], list) else False
                
                if tup[tmother] == "root":
                    root_correct = False
                    if child_is_list:
                        if root.text in tup[tchild]:
                            root_correct = True
                    elif root.text == tup[tchild]:
                        root_correct = True
                    else:
                        test_stuff.logger(f"\t\t\t\t {root.text} != {tup[tmother]}")

                    if root_correct:
                        found_mother = True
                        found_child = True
                        found_deprel = True

                else:
                    #see if you find current tuple in t
                    for word in tree.words:
                        #check if word is a child node
                        if child_is_list:
                            if word.text in tup[tchild]:
                                found_child = True
                        else:
                            if word.text == tup[tchild]:
                                found_child = True
                        #check if mother and deprel match
                        
                        #mother is a dictionary, just like a word
                        mother = get_word(f"{word.head}", tree.words)
                        
                        if isinstance(mother, str):
                            mother_text = mother
                        else:
                            mother_text = mother.text
                            found_mother = True

                        if mother_text == tup[tmother]:
                            #check if deprel matches
                            if deprel_is_list:
                                if word.deprel in tup[tdeprel]:
                                    found_deprel = True
                            else:
                                if word.deprel == tup[tdeprel]:
                                    found_deprel = True
                        if found_mother and found_deprel and found_child:
                            break
                if found_mother and found_deprel and found_child:
                    test_stuff.logger("\t\t\t\t\t Tupel correct!")
                    correct_tupel_counter += 1
            if correct_tupel_counter == len(dep_template):
                test_stuff.logger(f"///Found match ({d['id']}): {dep_template}\n")
                return f"///Found match: {dep_template}\n"
            else:
                test_stuff.logger(f"NO MATCH. mother: {found_mother}, deprel: {found_deprel}, child: {found_child}")


                '''
                ("root", "root", "predicted"),
                ("predicted", "nsubj:pass", f"upos{category_tag}NOUN")
                '''


def sentence_similarity(sent1, sent2, pipeline):
    t1 = pipeline(sent1).sentences[0]
    t2 = pipeline(sent2).sentences[0]

    total, percent = tree_compare(t1, t2)
    return total, percent

def print_depparsed_sentences(sentences, language="en", pipeline=""):
    if not pipeline:
        pipeline = init_stanza(language)
    if isinstance(sentences, str):
        sentences = [sentences]
    output, roots = depparse(sentences, pipeline)
    for o in output:
        print(o)
    
def debug_depparsed_sentences_to_console():
    pipeline = init_stanza("en")
    
    eric = eric_nlp.Eric_nlp()
    sentence_list = ["Used sentences:"]
    
    print("Please provide input:")
    while True:
        usr_in = input()
        
        if not usr_in:
            print("no input given")
            continue
        elif usr_in.lower() in ["exit", "exit()", "quit", "quit()", "end", "end()"]:
            break
        
        sentence_list.append(usr_in)
        preprocessed = eric.preprocessing(usr_in, "usr_input")
        print(f"preprocessed: {preprocessed}")

        # tree = pipeline(preprocessed).sentences[0]
        # results = get_matching_dictionary_trees(tree, eric)
        # print(results)
        # continue
        out, roots = depparse([preprocessed], pipeline)

        root = ""
        for o in out:
            if "id: 0" in o:
                finder = "word: "
                ender = "lemma: "
                index = o.find(finder) + len(finder)
                index_end = o.find(ender)

                root = o[index:index_end].strip()


        if not root:
            root = "root not found"

        print(f"Root: {root}")
        for o in out[3:]:
            print(o)
    print("Goodbye")
    for sent in sentence_list:
        print(sent)
    

def main():
    input_language = "en"
    stanza_pipeline = init_stanza(input_language)
    eric = eric_nlp.Eric_nlp()
    input_path = "data\\"
    input_files = [f"{input_path}umfrage_input_{x}_cleaned.txt" for x in range(1,5)]
    input_files.append(f"{input_path}manually_added.txt")
    output_path = "output\\depparse\\data_analysis\\"
    roots_out_file = f"{output_path}roots.csv"

    input_accumulated = test_stuff.merge_input_files(input_files)#{x["id"]: x["key_sentences"] for x in dictionary}
    input_accumulated = list(set(input_accumulated))
    input_accumulated_as_dict = {}
    for x in input_accumulated:
        if x[0] in input_accumulated_as_dict.keys():
            input_accumulated_as_dict[x[0]].append(x[1])
        else:
            input_accumulated_as_dict[x[0]] = [x[1]]
    all_roots = dict() #keys are root words and the values are dicts where the keys are the function_id
    for fct_id, unpreprocessed_sentences in input_accumulated_as_dict.items():
        preprocessed_sentences = [eric.preprocessing(x, "usr_input") for x in unpreprocessed_sentences]
        out_file = f"{output_path}{fct_id}.txt"
        dep_output, roots = depparse(preprocessed_sentences, stanza_pipeline)
        
        preface = [f"{v}: {k}" for k, v in roots.items()]
        
        #extend all_roots
        all_roots = extend_roots(all_roots, roots, fct_id)


        all_output = ["Used Input:"] + input_files + ["\n"] + preface + dep_output
        for o in all_output:
            print(o)
        #test_stuff.list_to_file(all_output, out_file)

    create_roots_matrix(all_roots, roots_out_file, empty_cell="")
    print(all_roots)




    #for infi in input_files:
        # input_data = 
        # test_input = [x[1] for x in test_stuff.read_input_from_file(f[0])]
        # test_output = depparse("en", test_input)
        # test_stuff.list_to_file(test_output, f[1])

def read_sentences_from_output(output_file):
    stop_words = ["OUTPUT:", "Root:", "id:"]
    file_lines = test_stuff.get_file_lines(output_file)
    sentences = list()
    for line in file_lines:
        if line != "":
            if not line[0].isdigit() and line[0] != "=":
                splitted = line.split()
                if splitted[0] not in stop_words:
                    sentences.append(line)
    return list(set(sentences))




'''
if you thought of new sentence while analysing the output and just depparsed them over debug console and included them in the output_file, 
this function will help. It can read your originally used input again, then the output file, compare sentences and store all new ones, i.e. the manually analysed sentences in a new input_file.
Also, it will then overwrite the output file to update the root counts
'''
def update_depparse_output(input_files, output_file_overwrite, passed_fct_id, output_file_new_sentences="data\\manually_added.txt", sp=""):
    #input_accumulated.extend([("why", "Why did you predict this outcome?"), ("why", "Why did you predict the outcome?")])

    #1 get all three as dictionaries {passed_fct_id: list of sentences}
    #1.1 originally used input
    lines = test_stuff.merge_input_files(input_files)
    lines = list(set(lines))
    input_accumulated = convert_input_tuples_to_dict(lines)
    #1.2 modified output
    lines = read_sentences_from_output(output_file_overwrite)
    output_accumulated = {passed_fct_id: lines}
    #1.3 existing manually added sentences
    lines = test_stuff.merge_input_files([output_file_new_sentences])
    lines = list(set(lines))
    manual_accumulated = convert_input_tuples_to_dict(lines)

    #2 look for sentences in output_accumulated, that do not exist in input_accumulated and append these to manual_accumulated if they not already exist there
    eric = eric_nlp.Eric_nlp()
    for fct_id, sentences in output_accumulated.items():
        if fct_id in input_accumulated.keys():
            preprocessed_inputs = [eric.preprocessing(x, "usr_input") for x in input_accumulated[fct_id]]
            for sent in sentences:
                sentence = eric.preprocessing(sent, "usr_input")
                if sentence not in preprocessed_inputs:
                    if fct_id in manual_accumulated.keys():
                        if sentence not in manual_accumulated[fct_id]:
                            manual_accumulated[fct_id].append(sentence)
                    else:
                        manual_accumulated[fct_id] = [sentence]
        else:
            #all are new sentences
            if fct_id in manual_accumulated.keys():
                if sentence not in manual_accumulated[fct_id]:
                    manual_accumulated[fct_id].append(sentence)
            else:
                manual_accumulated[fct_id] = [sentence]

    #4 write manual_accumulated to data\\manually_added.txt (or sth else, if argument was given)
    out= []
    for fct_id, sentences in manual_accumulated.items():
        out.append(f"[{fct_id}]")
        out.extend(sentences)
        out.append("")
    test_stuff.list_to_file(out, output_file_new_sentences)

    #5 update the output file
    #5.1 get all sentences for fct_id from manually_added.txt and the input files
    if not sp:
        sp = init_stanza("en")
    all_sentences = []
    if passed_fct_id in manual_accumulated.keys():
        all_sentences.extend(manual_accumulated[passed_fct_id])
    if passed_fct_id in input_accumulated.keys():
        all_sentences.extend(input_accumulated[passed_fct_id])

    all_sentences = [eric.preprocessing(x, "usr_input") for x in all_sentences]
    out, roots = depparse(all_sentences, sp)
    preface = [f"{v}: {k}" for k, v in roots.items()]

    all_out = preface + out
    test_stuff.list_to_file(all_out, output_file_overwrite)

def convert_input_tuples_to_dict(input_tuples):
    ret_val = dict()
    for fct_id, sentence in input_tuples:
        if fct_id in ret_val.keys():
            if sentence not in ret_val[fct_id]:
                ret_val[fct_id].append(sentence)
        else:
            ret_val[fct_id] = [sentence]
    return ret_val

def test_some_sentences():
    sp = init_stanza("en")
    sentences = []

    words = ["more", "less", "lower", "higher", "greater"]

    more = [f"what if fare was {x} than 300 instead" for x in words]
    sentences.extend(more)

    more = [f"what if age was {x} than 44 instead" for x in words]
    sentences.extend(more)

    more = [f"what if age was {x} 44" for x in ["over", "under"]]
    sentences.extend(more)
    
    more = [f"what if age was {x}" for x in words]
    sentences.extend(more)

    out, roots = depparse(sentences, sp)

    for o in out:
        print(o)
    

if __name__ == "__main__":
    #main()

    debug_depparsed_sentences_to_console()
    quit()

    lines = test_stuff.read_input_from_file("data\\wrongly_accused.txt")
    sentences = [x[1] for x in lines]
    for s in sentences:
        print(s)
    print("//////////")
    sp = init_stanza("en")
    out, root = depparse(sentences, sp)
    test_stuff.list_to_file(out, "output\\depparse\\wrongly_accused_out.txt")
    quit()
    
    #test_some_sentences()

    for d in dictionary:
        print(d["id"])
        try:
            x = d['depparse'][0]
            print("\t---")
        except:
            print("\tNOTHING")

    sp = init_stanza("en")
    input_files = [f"data\\umfrage_input_{x}_cleaned.txt" for x in range(1,5)]
    fct = "whatif-gl"
    update_depparse_output(input_files, f"output\\depparse\\{fct}.txt", fct, "data\\manually_added.txt", sp=sp)
