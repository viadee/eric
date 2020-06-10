import eric_nlp
from dictionary import dictionary, nlp_dictionary
import copy
from datetime import datetime
import time
import depparse
#from depparse import init_stanza
from datetime import datetime
import sys
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
                        x = (current_id, line)
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
    for file_name in file_list:
        print(f"reading file: {file_name}")
        file_content = read_input_from_file(file_name)
        for fc in file_content:
            fct_id = fc[0]
            sentence = fc[1]
            ret_val.append((fct_id, sentence))
    
    return list(set(ret_val))

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




model_path = "data\\"
models = ["wiki.en.bin"]#, "wiki_bigrams.bin", "torontobooks_unigrams.bin", "wiki_unigrams.bin", "cc.en.300.bin"]
methods = ["minkowski"]#, "euclidean", "braycurtis", "chebyshev", "correlation", "cosine", "sqeuclidean"]


# lines = get_file_lines("output\\logger2.txt")
# list_to_file([x for x in lines if "DEPREPLACE" in x], "output\\logger2.txt")
# quit()


if __name__ == "__main__":
    #sys.stdout = open(log_file, "w")

    

    in_files = [f"data\\umfrage_input_{x}_cleaned.txt" for x in range(1,5)]
    models = [f"{model_path}{model}" for model in models]
    eric = eric_nlp.Eric_nlp()
    sp = depparse.init_stanza("en")


    similarity_depparse_combination(eric, models[0], methods[0], "output\\TESTSET\\", "testset", in_files, True, sp)

    #print("Starting Test")
    #tester("similarity", eric, models, methods, "output\\similarity_retest\\", "similarity_retest", in_files, True, sp)
    #print("main2")
    #tester("depparse", eric, models, methods, "output\\depparse_dictionary_templates_test\\", "Blabla", in_files, False, sp)
