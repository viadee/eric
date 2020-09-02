import eric_nlp
from dictionary import dictionary, nlp_dictionary
import copy
from datetime import datetime
import time
import scipy
import depparse
#from depparse import init_stanza
from datetime import datetime
import sys, os
log_file = "output\\logger2.txt"


input_from_console = False
output_path = "output\\"
test_input = [
    ("init", "Hello"),
    ("predict", "Please make a prediction."),
    ("predict", "prediction"),
    ("predict", "Would you predict something for me?"),
    ("whatif", "What if you changed Sex to Male?"),
    ("whatif", "What if Age was 24?"),
    ("whatif", "What if age 33"),
    ("featureNames", "can you show me what you use as input?"),
    ("featureNames", "What are your parameters?"),
    ("preview", "do you have any samples?"),
    ("whatif-gl", "what if age was greater?"),
    ("whatif-gl", "what if relatives was different?"),
    ("when", "When do you change your prediction?"),
    #input with unacceptable parameters
    ("whatif", "What if Relatives was 999"),
    ("whatif", "What if Age was -3.6?"),
    ("none", "Hey, I just wanted to chat with you."),
    #nonsense input
    ("none", "I want to eat some sandwiches!"),
    ("none", "You want to eat some sandwiches!"),
    ("none", "The earth is actually flat"),
    ("none", "These aren't the droids you are looking for."),
    ("none", "Belinda blinked, it wasn't a dream."),
    ("none", "Cann you predict the weather?")
]

#takes filename, returns list of tupels (<should-be-result>, <sentence to test>)
#file is expected as a txt with one sentence per line. A line with square brackets like [x] changes current <should-be-result> to x
def read_input_from_file(file_name):
    ret_val = list()
    current_id = "no_id_given"
    lines = [line for line in get_file_lines(file_name) if line != ""]
    for line in lines:
        if line.strip():
            if line.lstrip()[0] != "#":
                if line[0] == "[" and line[-1] == "]":
                    current_id = line[1:-1]
                else:
                    if line.strip() != "":
                        x = (current_id, line, file_name)
                        ret_val.append(x)
    return ret_val


#takes filename, returns list of lines (as string) of that file
def get_file_lines(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        try:
            x = f.read()
        except IOError as e:
            print(e)
            quit()
    return x.split("\n")

def list_to_file(the_list, filename, mode="w", encoding="utf-8"):
    if not isinstance(the_list, list):
        the_list = [the_list]
    with open(filename, mode, encoding=encoding) as f:
        for row in the_list:
            f.write(f"{row}\n")
    if mode != "a":
        print(f"wrote list to {filename}")

#reads a given eric log and looks for the messages that came from the front end. then writes all of them line by line to a given output file
def extract_usr_input_from_eric_log(in_file, out_file):
    all = []
    lines = get_file_lines(in_file)
    for l in lines:
        if "Text message received" in l:
            index = l.find("{")
            as_dict = eval(l[index:])
            all.append(as_dict["answer"])
    list_to_file(all, out_file)


#test sentences should be a list of tuples (function_id_gold, the_sentence)
def similarity_tester(method, limit, eric, output_file, test_sentences="", comment=["No comment given", "Make sense of it on your own", "Text speaks for itself"]):
    used_key_sentences = {x["id"]: x["key_sentences"] for x in nlp_dictionary}
    out_all = [
        f"Every entry shows a timestamp, then the input sentence and the top {limit} matches that were found (if that many exist).",
        "entries sorted by <CALCULATED>. The other column headline in <> is the algorithm that was used.",
        "\n"
    ]
    out_all.append("//// BEGIN Test comments ////")
    out_all.extend(comment)
    out_all.append("//// END Test comments ////\n\n")

    out_all.append("//// BEGIN Preprocessing overview ////")
    for pm, on_off in eric.preprocessing_methods.items():
        out_all.append(f"{pm}: {on_off[0]}")
    out_all.append("//// END Preprocessing overview ////\n\n")

    out_all.append("//// BEGIN Key Sentence overview ////")
    for k, v in used_key_sentences.items():
        out_all.append(f"{k}")
        out_all.extend([f"\t{x}" for x in v])
    out_all.append("//// END Key Sentence overview ////\n\n")


    out_all.extend(["\n================", "//// BEGIN Output ////\n"])

    out = ["no output exists"]

    #######
    ### CONSOLE
    #######
    print("---START---")
    #read from console if no test_sentences were provided
    if not isinstance(test_sentences, list):
        input_counter = 1
        console_loop = True
        while console_loop:
            usr_in = input()
            if usr_in.lower() in ["exit", "exit()", "quit", "quit()", "end", "end()"]:
                console_loop = False
            choice, certainty, out = eric.method_comparison(usr_in, method=method, limit=limit)
            out.insert(0, f"certainty: {certainty}")
            out.insert(0, f"{input_counter}: {datetime.now()}")
            input_counter += 1
            out.append("=====================\n\n")
            #extend file every time
            out_all.extend(out)
            for o in out:
                print(o)
            
            #exit from loop and save to file if wanted
            if not console_loop:
                save_successful = False
                prompt = "Do you want to save the output to a file? (y/n)"
                while not save_successful:
                    print(prompt)
                    usr_in = input()
                    if usr_in.lower() in ["n", "no"]:
                        print("Output was not saved.")
                        save_successful = True
                    elif usr_in.lower() in ["y", "yes"]:
                        try:
                            list_to_file(out_all, output_file)
                            print(f"Saved output to {output_file}")
                            save_successful = True
                        except IOError as e:
                            print(f"Failed to save output to {output_file}")
                            print(e)
                            prompt = "Do you want to try again? (y/n)"

    #######
    ### FROM FILE
    #######
    else:
        sentence_count = len(test_sentences)
        wrong_counter = 0
        for line, index in zip(test_sentences, range(sentence_count)):
            gold, sentence = line
            #cosmetic
            loading_bar = f"({index+1}/{sentence_count})"

            choice, certainty, out = eric.method_comparison(sentence, method=method, limit=limit)
            deny_certainty = (eric.deny_threshold - choice[1]) * 100.0 #negative if correctly accepted
            if choice[1] < eric.deny_threshold:
                if line[0] == "none":
                    correct = "CORRECTLY denied"
                else:
                    correct = f"WRONGLY denied. Should have been {gold}"
                    wrong_counter += 1
            else:
                if choice[0] == gold:
                    correct = "CORRECT matching"
                else:
                    correct = f"WRONG matching. Should have been {gold}"
                    wrong_counter += 1

            #correct = f"eric chose the {correct} function." if line[0] else "The input could not have yielded a correct answer" 
            out.insert(0, f"deny certainty: {deny_certainty}")
            out.insert(0, f"certainty: {certainty}")
            out.insert(0, correct)
            out.insert(0, f"{loading_bar} {datetime.now()}")
            out.append("=====================\n\n")

            out_all.extend(out)
            print(f"done{loading_bar}: {line}")
        #write everything at once
        wrong_percent = wrong_counter * 100.0 / sentence_count
        out_all.insert(0, f"wrong count: {wrong_counter}/{sentence_count} (~{wrong_percent}%)")
        out_all.append("//// END Output ////")
        list_to_file(out_all, output_file)
    print("---END---")


#returns list of tuples (fct_id, sentence) with no duplicates
def merge_input_files(file_list):
    ret_val = []
    if not isinstance(file_list, list):
        file_list = [file_list]
    for file_name in file_list:
        print(f"reading file: {file_name}")
        file_content = read_input_from_file(file_name)
        for fc in file_content:
            fct_id = fc[0]
            sentence = fc[1]
            origin = fc[2]
            ret_val.append((fct_id, sentence, origin))
    
    #filter out duplicates, disregarding origin
    ret_val_no_duplicates = []
    for fct_id, sentence, origin in ret_val:
        exists = False
        for x in ret_val_no_duplicates:
            if fct_id == x[0] and sentence == x[1]:
                exists = True
                break
        if not exists:
            tpl = (fct_id, sentence, origin)
            ret_val_no_duplicates.append(tpl)
    return ret_val_no_duplicates

#returns list with tuples (fct_id, key_sentence, tree) for all key_sentences for all functions in dictionary.nlp_dictionary
def get_key_sentence_depparse_trees(eric_instance, stanza_pipeline):
    ret_val = []
    for d in nlp_dictionary:
        for key_sentence in d["key_sentences"]:
            ks = eric_instance.preprocessing(key_sentence, "key_sentence")
            ks_tree = stanza_pipeline(ks).sentences[0]

            ks_tuple = (d["id"], ks, ks_tree)
            ret_val.append(ks_tuple)
    return ret_val

def logger(output):
    with open(log_file, encoding="utf-8", mode="a") as f:
        ts = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        if not isinstance(output, list):
            output = [output]
        for o in output:
            f.write(f"{ts} // {o}\n")

#sp is the stanza pipeline
def depparse_tester(eric, sp, output_file, sentence_tuples):
    all_out = []
    for gold, sent in sentence_tuples:
        sentence = eric.preprocessing(sent, "usr_input")
        tree = sp(sentence).sentences[0]
        print(f"sentence: {sentence}")
        results = depparse.get_matching_dictionary_trees(tree, eric)
        all_out.append(f"({gold}) {sentence}:")
        first = True
        if results:
            #all_out.append(f"LEN > 0: {results}")
            for fct, template in results:
                if first:
                    first = False
                    tab = "\t CORRECT \t" if gold == fct else "\t WRONG \t"
                else:
                    tab = "\t"
                #if "CORRECT" not in tab:
                all_out.append(f"{tab}{fct}: {template}")
        else:
            tab = "\t CORRECTLY denied \t" if gold == "none" else "\t WRONGLY denied \t"
            #if "CORRECT" not in tab:
            all_out.append(tab)
        all_out.append("")
    list_to_file(all_out, output_file)


def eric_matching_from_console(eric, sp):
    console_loop = True
    while console_loop:
        usr_in = input()
        if usr_in.lower() in ["exit", "exit()", "quit", "quit()", "end", "end()"]:
            console_loop = False
        else:
            result = eric.map_to_eric_function(usr_in)
            print(f"Result: {result}")

    print("Goodbye.")

'''
explanation of arguments:
    kind: what functionality should be evoced? one of ["similarity", "depparse"]
    models: list of filenames of pretrained eric models. models should be in ./data
    methods: list of method names that should be used. see eric_nlp.get_similarity_ranking()
    output_path: path were output files should be written to, including final "\\"
    output_name: a name, all output files should be named. output files will be called f"{output_name}_x.txt" with x being iterated depending on how many input files there are.
    in_files: list of txt-files that should be read for user input. see test_stuff.merge_input_files() and test_stuff.read_input_from_file()
    merge_in_files: if you want all input files to be merged into one, so that only one output file will be generated, set this to True
'''
def tester(kind, eric, models, methods, output_path, output_name, in_files, merge_in_files, stanza_pipeline="", lang="en"):
    if merge_in_files:
        test_inputs = {f"{output_name}_merged": merge_input_files(in_files)}
    else:
        test_inputs = {f"{output_name}_{x+1}": read_input_from_file(f) for x, f in enumerate(in_files)}
    print("done reading files")
    # test_inputs = {"sample": [
    #     ("whatif", "what would happen if they were in first class instead"),
    #     ("when", "when is a person died survived")
    # ]}

    if kind == "similarity":
        for test_name, test_sentences in test_inputs.items():
            print(f"similarity test: {test_name}")
            for model in models:
                if eric.model != model:
                    eric.load_model(model)
                for method in methods:
                    similarity_tester(method, 10, eric, f"{output_path}{test_name}.txt", test_sentences)
        
    elif kind == "depparse":
        sp = depparse.init_stanza(lang) if not stanza_pipeline else stanza_pipeline
        for test_name, test_sentences in test_inputs.items():
            print(f"depparse test: {test_name}")
            depparse_tester(eric, sp, f"{output_path}{test_name}.txt", test_sentences)
    else:
        print(f"unknown kind: {kind}")
    

def similarity_depparse_combination(eric, model, method, output_path, output_name, in_files, merge_in_files, stanza_pipeline="", lang="en"):
    sp = depparse.init_stanza(lang) if not stanza_pipeline else stanza_pipeline
    eric = eric_nlp.Eric_nlp()
    eric.method = method
    print(f"eric model '{model}' loading")
    eric.load_model(model)
    print(f"eric model '{model}' loaded")

    if merge_in_files:
        test_inputs = {f"{output_name}_merged": merge_input_files(in_files)}
    else:
        test_inputs = {f"{output_name}_{x+1}": read_input_from_file(f) for x, f in enumerate(in_files)}
    print("done reading files")

    print("\n")
    all_out = []
    correct_count = 0
    correct_count_no_depparse = 0
    wrong_but_denied_count = 0
    for test_name, test_tuples in test_inputs.items():
        print(f"{test_name}:")
        for gold, sentence in test_tuples:
            out = []
            depparse_necessary = False
            preprocessed_sentence = eric.preprocessing(sentence, "usr_input")
            similarity_ranking = eric.get_similarity_result(preprocessed_sentence, limit=5)
            #tuple (fct_id, matching similarity)
            similarity_result = (similarity_ranking[0][0], similarity_ranking[0][1])
            result = similarity_result[0]
            if similarity_result[1] < eric.depparse_threshold:
                depparse_necessary = True
                preprocessed_depparse_sentence = eric.preprocessing(sentence, "usr_input")
                tree = sp(preprocessed_depparse_sentence).sentences[0]
                depparse_ranking = depparse.get_matching_dictionary_trees(tree, eric)
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
                depparse_result = ("none", [f"No depparsing necessary; similarity >= depparse_threshold ({similarity_result[1]} >= {eric.depparse_threshold})"])

            if depparse_result[0] == "none" and similarity_result[1] < eric.deny_threshold:
                result = "none"

            if result == gold:
                correctness = True
                correctness_phrase = "CORRECT"
                correct_count += 1
            else:
                correctness_phrase = "WRONG"
                correctness = False
                if result == "none":
                    wrong_but_denied_count += 1

            out.extend(
                [
                    "",
                    f"{'/'*40}",
                    f"       sentence: {sentence}",
                    f"         result: {result}",
                    f"           gold: {gold}",
                    f"    correctness: {correctness_phrase}",
                    f" did depparsing: {depparse_necessary}",
                    f"   simil-result: {similarity_result}",
                    f"depparse-result: {depparse_result}"
                ]
            )
            if depparse_necessary:
                results_were_equal = "True" if depparse_result[0] == similarity_result[0] else "False"
                out.extend(
                    [
                        f"  results equal: {results_were_equal}"
                    ]
                )
            else:
                if correctness:
                    correct_count_no_depparse += 1


            all_out.extend(out)
            for o in out:
                print(o)
        
        sentence_count = len(test_tuples)
        correct_percent = correct_count * 100.0 / sentence_count
        wrong_count = sentence_count - correct_count
        wrong_percent = wrong_count * 100.0 / sentence_count

    
        preface = [
            f"                   CORRECT: {correct_count} / {sentence_count} ({correct_percent}%)",
            f"                     WRONG: {wrong_count} / {sentence_count} ({wrong_percent}%)",
            f"Correct without depparsing: {correct_count_no_depparse}",
            f"          Wrong but denied: {wrong_but_denied_count}",
            "\n"
        ]
        preface.extend(all_out)
        list_to_file(preface, f"{output_path}{test_name}.txt")

#get a set of all depparse relations that exist in the nlp_dictionary
def get_all_depparse_relations():
    ret_val = set()
    for dct in nlp_dictionary:
        for tpl_list in dct["depparse"]:
            for tpl in tpl_list:
                if isinstance(tpl[1], str):
                    ret_val.add(tpl[1])
                elif isinstance(tpl[1], list):
                    for l in tpl[1]:
                        ret_val.add(l)
                else:
                    print(f"ERROR. unknown depparse relation format. Expected list or str, but received {type(tpl[1])}")
    return ret_val
        
def count_depparse_templates():
    counter = dict()
    count_total = 0
    for fct_dict in nlp_dictionary:
        count = 0
        for node_list in fct_dict["depparse"]:
            count += 1
        counter[fct_dict["id"]] = count
        count_total += count
    
    print(f"Total: {count_total}")
    for k, v in counter.items():
        print(f"{k}: {v}")


def compare_similarity_models(models, model_path, sentences):
    disable_print_function()
    sent_count = len(sentences)
    eric = eric_nlp.Eric_nlp()
    out = []
    for model in models:
        wrong_out = ["{sim_result[0]}|{result}|{gold}: '{sent}' => {origin} ({sim_result[1][0]})"]
        wrong_out_result_none = ["", "", ""]
        wrong_out_gold_none = ["", "", ""]
        eric.load_model(f"{model_path}{model}")
        correct_count = 0
        for gold, sent, origin in sentences:
            result, sim_result, dep_result, time_elapsed = eric.map_to_eric_function(sent, analytics=True)
            if sim_result[0] == gold:
                correct_count += 1
            else:
                print(f"'{sim_result[0]}' != '{gold}'")
                if result == gold:
                    print(f"     but {result} == {gold}")
                elif gold == "none":
                    wrong_out_gold_none.append(f"{sim_result[0]}|{result}|{gold}: '{sent}' => {origin} ({sim_result[1][0]})")
                elif result == "none":
                    wrong_out_result_none.append(f"{sim_result[0]}|{result}|{gold}: '{sent}' => {origin} ({sim_result[1][0]})")
                else:
                    wrong_out.append(f"{sim_result[0]}|{result}|{gold}: '{sent}' => {origin} ({sim_result[1][0]})")

        correct_percent = correct_count * 100.0 / sent_count
        out.append(f"Model '{model}': {correct_count}/{sent_count} correct ({correct_percent}%)")
        print(f"Model '{model}': {correct_count}/{sent_count} correct ({correct_percent}%)")
        wrong_out.insert(0, f"Model '{model}': {correct_count}/{sent_count} correct ({correct_percent}%)")
        wrong_out.extend(wrong_out_result_none)
        wrong_out.extend(wrong_out_gold_none)
        list_to_file(wrong_out, f"D:\\Bachelor\\eric\\output\\dev_results_{model}.txt")
    
    for o in out:
        print(o)

def disable_print_function():
    sys.stdout = open(os.devnull, 'w')

def enable_print_function():
    sys.stdout = sys.__stdout__

def evaluate_threshold(sentences, eric, sp):
    # (best accuracy, depparse_threshold, deny_threshold)
    out_path = "D:\\Bachelor\\eric\\output\\threshold_analysis\\"
    sent_count = len(sentences)
    best_accuracy = (0.0, 0.0, 0.0)
    best_accuracies = [best_accuracy] #in case multiple combinations result in the same accuracy

    min_threshold = 8100
    max_threshold = 8400
    increment = 1
    #for dep_int in range(min_threshold, max_threshold, increment):
    # dep = 100.0
    for deny_int in range(min_threshold, max_threshold, increment):
        # if deny_int > dep_int:
        #     print(f"(<skipped>,{dep},{deny})")
        #     continue
        # deny = (150.0-deny_int) / 10
        deny = (15000.0-deny_int) / 10000
        eric.deny_threshold = deny
        print(f"Trying: dep={eric.depparse_threshold*100.0}% | deny = {eric.deny_threshold*100.0}%")
        disable_print_function()
        # eric.deny_threshold = deny
        
        # correct_count = 0
        # for gold, sent, origin in sentences:
        #     result = eric.map_to_eric_function(sent)
        #     if gold == result:
        #         correct_count += 1
        output, total_count, correct_count, accuracy, confusion = analyze_sentences(sentences, eric, sp, sendback_accuracy=True)
        # accuracy = correct_count / sent_count

        if accuracy > best_accuracy[0]:
            best_accuracy = (accuracy, eric.depparse_threshold, eric.deny_threshold)
            best_accuracies = [best_accuracy]
            out2 = f" NEW BEST ({correct_count}/{sent_count} correct)"
        elif accuracy == best_accuracy[0]:
            best_accuracies.append((accuracy, eric.depparse_threshold, eric.deny_threshold))
            out2 = f"Just as good ({correct_count}/{sent_count} correct)"
        else:
            out2 = "Worsened"
        
        out = f"({accuracy},{eric.depparse_threshold},{eric.deny_threshold}) {out2}"
        enable_print_function()
        print(out)
        list_to_file(output, f"{out_path}thresh_dep{eric.depparse_threshold}_den{eric.deny_threshold}.txt")
        disable_print_function()
    
    enable_print_function()
    print("\nBest Result:")
    print("(accuracy, dep, deny)")
    for ba in best_accuracies:
        print(ba)



def analyze_sentences(sentences, eric, sp, sendback_accuracy=False):
    time_min = -1.0
    time_min_sentence_id = 0
    time_max = 0.0
    time_max_sentence_id = 0
    total = len(sentences) if len(sentences) > 0 else 1
    correct = 0
    wrong_but_denied = 0
    denied = 0
    wrongly_denied = 0
    wrongly_accepted = 0
    similarity_correct = 0
    depparse_necessary = 0
    depparse_correct = 0
    confusion_matrix = {"none": {"none": 0}}#key: fct_id, value: dictionary with key=fct_id and value as count => matrix has as many columns and rows as there are function (+1 for "none")
    #initiate for all functions
    for fct_dict in nlp_dictionary:
        confusion_matrix["none"][fct_dict["id"]] = 0

        confusion_matrix[fct_dict["id"]] = dict()
        confusion_matrix[fct_dict["id"]]["none"] = 0
        for fct_dict2 in nlp_dictionary:
            confusion_matrix[fct_dict["id"]][fct_dict2["id"]] = 0
    
    
    output_wrong = []
    output_correct = [
        "="*30,
        "="*30
    ]
    time_total = 0.0
    sentence_count = 0
    time_elapsed_dict = dict() #maps sentence_id to time_elapsed for that sentence
    for gold, sent, origin in sentences:
        sentence_count += 1
        dep_status = "depNone"
        #sim_result is: tuple (fct_id, tuple(similarity in percent, matched key_sentence_original, matched_keysentence_with_replaced_placeholders))
        #dep_result is: tuple (fct_id, depparse_demplate that matched as list of tuples)
        result, sim_result, dep_result, time_elapsed = eric.map_to_eric_function(sent, analytics=True)
        time_elapsed_dict[sentence_count] = (time_elapsed, sent)

        time_total += time_elapsed
        if time_min < 0:
            time_min = time_elapsed
            time_max = time_elapsed
            time_min_sentence_id = sentence_count
            time_max_sentence_id = sentence_count
        else:
            if time_min > time_elapsed:
                time_min = time_elapsed
                time_min_sentence_id = sentence_count
            if time_max < time_elapsed:
                time_max = time_elapsed
                time_max_sentence_id = sentence_count


        if sim_result[0] == gold:
            similarity_correct += 1
            sim_status = "simCORRECT"
        else:
            sim_status = "simWRONG"
        if result == gold:
            correct_status = "CORRECTly denied" if gold == "none" else "CORRECT"
            correct += 1
        else:
            correct_status = "WRONGly denied" if result == "none" else "WRONG"
            if gold == "none":
                wrongly_accepted += 1
            elif result == "none":
                wrongly_denied += 1
        if sim_result[1][0] < eric.depparse_threshold:
            depparse_necessary += 1
            if dep_result[0] == gold:
                depparse_correct += 1
                dep_status = "depCORRECT"
            else:
                dep_status = "depWRONG"
        if result == "none":
            denied += 1
            if gold != "none":
                wrong_but_denied += 1

        #CONFUSION MATRIX
        confusion_matrix[result][gold] += 1
       
        
        
        prepped_sentence = eric.preprocessing(sent, "usr_input")
        out_add = [
            "="*31,
            f"        ID: {sentence_count}",
            f"plcholders: {eric.placeholders}"
            f"    timing: {time_elapsed}s",
            f"  Sentence: {sent}",
            f"   prepped: {prepped_sentence}",
            f"    Origin: {origin}",
            f"    Status: {correct_status}",
            f"sim_status: {sim_status}",
            f"dep_status: {dep_status}",
            f"      Gold: {gold}",
            f"    Result: {result}",
            f"Similarity: {sim_result}",
            f"  Depparse: {dep_result}"
        ]

        if result == gold:
            output_correct.extend(out_add)
        else:
            output_wrong.extend(out_add)
    
    wrong = total - correct
    correct_ratio = correct * 100.0 / total
    wrong_ratio = 100.0 - correct_ratio
    similarity_correct_ratio = similarity_correct * 100.0 / total
    if depparse_necessary > 0:
        depparse_correct_ratio = depparse_correct * 100.0 / depparse_necessary
    else:
        depparse_correct_ratio = "n/A"
    time_average = time_total / float(total)
    preface = [
        f"         correct: {correct}/{total} ({correct_ratio}%)",
        f"           wrong: {wrong}/{total} ({wrong_ratio}%)",
        f"wrong but denied: {wrong_but_denied}",
        f"   depparse done: {depparse_necessary}",
        f"     sim_correct: {similarity_correct}/{total} ({similarity_correct_ratio})",
        f"   depp. correct: {depparse_correct}/{depparse_necessary} ({depparse_correct_ratio})",
        f"         Fastest: {time_min}s (ID: {time_min_sentence_id})",
        f"         Slowest: {time_max}s (ID: {time_max_sentence_id})",
        f"   average speed: {time_average}s / 1 sentence",
        f"total anal. time: {time_total}s"
    ]

    preface.extend(output_wrong)
    preface.extend(output_correct)
    if sendback_accuracy:
        time_elapsed_data = ["\n", "Sentence IDs and time elapsed for parsing them. Use as csv for plotting"]
        for k, v in time_elapsed_dict.items():
            time_elapsed_data.append(f"{k};{v[0]};{v[1]}")
        preface.extend(time_elapsed_data)
        return preface, total, correct, correct_ratio, confusion_matrix
    else:
        return preface

model_path = "data\\"
models = ["wiki.en.bin"]#, "wiki_bigrams.bin", "torontobooks_unigrams.bin", "wiki_unigrams.bin", "cc.en.300.bin"]
methods = ["minkowski"]#, "euclidean", "braycurtis", "chebyshev", "correlation", "cosine", "sqeuclidean"]


# lines = get_file_lines("output\\logger2.txt")
# list_to_file([x for x in lines if "DEPREPLACE" in x], "output\\logger2.txt")
# quit()


def evaluate_testset(input_file, model_file):
    sentences = merge_input_files(input_file)
    eric = eric_nlp.Eric_nlp()
    eric.load_model(model_file)
    sp = depparse.init_stanza("en")

    results = analyze_sentences(sentences, eric, sp)

    list_to_file(results, "D:\\Bachelor\\eric\\output\\testrestults_survey_8_to_11.txt")

def evaluate_fasttext_models(model_files, model_path, output_path, sentences):
    eric = eric_nlp.Eric_nlp()
    sp = depparse.init_stanza("en")
    comparison_dict = {"model": "accuracy"}

    for model in model_files:
        print("="*20)
        print(f"loading model: {model_path}{model}")

        time_start = time.time()
        eric.load_model(f"{model_path}{model}")
        time_end = time.time()

        model_load_string = f" Model Load Time: {time_end - time_start}s"

        disable_print_function()
        output, sent_count, correct_count, correct_ratio, confusion = analyze_sentences(sentences, eric, sp, sendback_accuracy=True)
        enable_print_function()

        output.insert(8, model_load_string)

        confusion_output = []
        tab = "\t"

        #v contains the counts how often k got predicted when v.key should have been predicted. so e.g. if result = predict, then v["predict"] has the true positives
        column_names = "\t\t"
        for k, v in confusion.items():
            out_str = f"{k}{tab}"
            column_names += f"{k}{tab}"
            for k2, v2 in v.items():
                out_str += f"{v2}{tab}"
            confusion_output.append(out_str)
        confusion_output.insert(0, column_names)
        confusion_output.append("")
        confusion_output.append("PRECISION AND RECALL PER FUNCTION")

        for k, v in confusion.items():
            confusion_output.append(f"[{k}]")

            tp = confusion[k][k] #true positive
            #tp_fp is sum of tp and the times k was predicted, when a different function was gold
            tp_fp = 0 
            for k_predicted in v.values():
                tp_fp += k_predicted
            #tp_fn is the number of all the times k should have been predicte, i.e. number of correct predictions + all the times something else was predicted when it should have been k
            tp_fn = 0
            for row in confusion.values():
                tp_fn += row[k]

            #CALCULATE
            precision = tp / tp_fp if tp_fp > 0 else "n/A"
            recall = tp / tp_fn if tp_fn > 0 else "n/A"
            f_measure = 2 * (precision * recall) / (precision + recall) if precision != "n/A" and recall != "n/A" else "n/A"
            
            confusion_output.append(f"Precision: {precision}")
            confusion_output.append(f"   Recall: {recall}")
            confusion_output.append(f"F-Measure: {f_measure}")
            confusion_output.append("")


        comparison_dict[model] = correct_ratio
        list_to_file(output, f"{output_path}{model}.txt")
        list_to_file(confusion_output, f"{output_path}{model}_confusion.txt")
        print(f"{correct_count}/{sent_count} correct. {correct_ratio}%")
        print()

    print("COMPARISON RESULTS:")
    for key, val in comparison_dict.items():
        print(f"{key}\t\t{val}")

def word_similarity_comparison_from_console(eric):
    splitter = ";;"
    console_loop = True
    while console_loop:
        print(f"Write two sentences, separated by '{splitter}'")
        usr_in = input()
        if usr_in.lower() in ["exit", "exit()", "quit", "quit()", "end", "end()"]:
            console_loop = False
        else:
            words = usr_in.split(splitter)
            if len(words) != 2:
                print(f"Error: Expected two sentences but received {len(words)}")

            else:
                w1 = words[0]
                w2 = words[1]
                vec1 = eric.get_word_vector(w1)
                vec2 = eric.get_word_vector(w2)
                svec1 = eric.get_sentence_vector(w1)
                svec2 = eric.get_sentence_vector(w2)
                
                sim = 1.0 - scipy.spatial.distance.minkowski(vec1, vec2)
                ssim = 1.0 - scipy.spatial.distance.minkowski(svec1, svec2)
                print(f"    Word 1: {w1}")
                print(f"    Word 2: {w2}")
                print(f"Similarity: {sim}")
                print(f"asSentence: {ssim}")

    print("Goodbye.")

def test_preprocessing():
    eric = eric_nlp.Eric_nlp()
    console_loop = True
    while console_loop:
        print(f"Write a sentence to test preprocessing")
        usr_in = input()
        if usr_in.lower() in ["exit", "exit()", "quit", "quit()", "end", "end()"]:
            console_loop = False
        else:
            preprocessed = eric.preprocessing(usr_in, "usr_input")
            print(f"preprocessed: '{preprocessed}'")
            print(f"placeholders: {eric.placeholders}")
            
    print("Goodbye.")


if __name__ == "__main__":
    count_depparse_templates()
    quit()
    model_path = "D:\\Bachelor\\eric\\data\\fasttext_models\\"
    model_file = "wiki.en.bin"
    # test_file = "D:\\Bachelor\\eric\\data\\survey\\umfrage_input_8_to_11_cleaned.txt"
    # evaluate_testset(test_file, f"{model_path}{model_file}")
    # quit()
    # eric = eric_nlp.Eric_nlp()
    # eric.load_model(f"{model_path}{model_file}")
    # word_similarity_comparison_from_console(eric)
    # quit()
    # sp = depparse.init_stanza("en")
    # eric_matching_from_console(eric, sp)



    test_input_file_name = "D:\\Bachelor\\bachelor_thesis_eric_nlp\\survey\\results_formatted.txt"
    dev_input_path = "D:\\Bachelor\\eric\\data\\survey\\"
    dev_input_file_names = [
        "umfrage_input_1_cleaned.txt",
        "umfrage_input_2_cleaned.txt",
        "umfrage_input_3_cleaned.txt",
        "umfrage_input_4_cleaned.txt",
        "umfrage_input_5_cleaned.txt",
        "umfrage_input_6_cleaned.txt",
        "umfrage_input_7_cleaned.txt"
        ]
    manually_added_file_name = "manually_added.txt"
    dev_input_file_names_pathed = [f"{dev_input_path}{x}" for x in dev_input_file_names]
    output_file_name = "D:\\Bachelor\\eric\\output\\dev_results.txt"

    eric = eric_nlp.Eric_nlp()
    # eric.load_model(f"{model_path}{model_file}")
    # sp = depparse.init_stanza("en")
    sentences = merge_input_files(dev_input_file_names_pathed)
    dev_sentence_count = len(sentences)
    manually_added_sentences = merge_input_files([f"{dev_input_path}{manually_added_file_name}"])
    sentences.extend(manually_added_sentences)
    manually_added_count = len(sentences) - dev_sentence_count
    # evaluate_threshold(sentences, eric, sp)
    # quit()

    model_list = [
        # "ag_news.ftz",
        # "ag_news.bin",
        # "amazon_review_full.bin"
        # "amazon_review_full.ftz",
        # "amazon_review_polarity.bin",
        # "amazon_review_polarity.ftz",
        # "dbpedia.ftz",
        # "dbpedia.bin"
         "cc.en.300.bin",
        "wiki.en.bin"
        # "wiki.en.align.vec",
        # "crawl-300d-2M.vec"
    ]
    output_path = "D:\\Bachelor\\eric\\output\\ft_model_comparison_with_confusion\\test2\\"
    # compare_similarity_models(model_list, model_path, sentences)
    sentences = merge_input_files([test_input_file_name])
    evaluate_fasttext_models(model_list, model_path, output_path, sentences)

    quit()
    # evaluate_threshold(sentences, eric, sp)
    # quit()
    results = analyze_sentences(sentences, eric, sp)

    output = ["used files:"]

    dev_input_file_names.append(manually_added_file_name)
    output.extend([f"    {x}" for x in dev_input_file_names])
    
    output.extend([
        f" dev_sentences: {dev_sentence_count}",
        f"manually added: {manually_added_count}"
    ])

    output.extend(results)

    list_to_file(output, output_file_name)

    #similarity_depparse_combination(eric, models[0], methods[0], "output\\TESTSET\\", "testset", in_files, True, sp)

    #print("Starting Test")
    #tester("similarity", eric, models, methods, "output\\similarity_retest\\", "similarity_retest", in_files, True, sp)
    #print("main2")
    #tester("depparse", eric, models, methods, "output\\depparse_dictionary_templates_test\\", "Blabla", in_files, False, sp)
