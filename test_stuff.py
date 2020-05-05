import eric_nlp
import stanza
import time
from datetime import datetime
input_from_console = False
output_path = "output\\"
output_file = "method_comparison.txt"
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
        if line[0] == "[" and line[-1] == "]":
            current_id = line[1:-1]
        else:
            x = (current_id, line)
            ret_val.append(x)
        
    return ret_val


#takes filename, returns list of lines (as string) of that file
def get_file_lines(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        x = f.read()
    return x.split("\n")

def list_to_file(the_list, filename, mode="w"):
    with open(filename, mode) as f:
        for row in the_list:
            f.write(f"{row}\n")
    print(f"wrote list to {filename}")


def tester(method, limit, eric, output_file, comment=["No comment given", "Make sense of it on your own", "Text speaks for itself"]):
    out_all = [
        f"Every entry shows a timestamp, then the input sentence and the top {limit} matches that were found (if that many exist).",
        "entries sorted by <CALCULATED>. The other column headline in <> is the algorithm that was used.",
        "\n",
        "//// BEGIN Test comments: ////"
    ]
    out_all.extend(comment)
    out_all.append("//// END Test comments: ////\n")
    out = ["no output exists"]
    
    print("---START---")
    if input_from_console:
        input_counter = 1
        while True:
            usr_in = input()
            if usr_in == "exit":
                break
            choice, certainty, out = eric.method_comparison(usr_in, method=method, limit=limit)
            out.insert(0, f"certainty: {certainty}")
            out.insert(0, f"{input_counter}: {datetime.now()}")
            input_counter += 1
            out.append("=====================\n\n")
            #extend file every time
            out_all.extend(out)
            for o in out:
                print(o)
            list_to_file(out_all, output_file)
    else:
        length = len(test_input)
        wrong_counter = 0
        for line, index in zip(test_input, range(length)):
            #cosmetic
            loading_bar = f"({index+1}/{length})"

            choice, certainty, out = eric.method_comparison(line[1], method=method, limit=limit)
            if choice[1] < eric.deny_threshold:
                if line[0] == "none":
                    correct = "CORRECTLY denied"
                else:
                    correct = f"WRONGLY denied. Should have been {line[0]}"
                    wrong_counter += 1
            else:
                if choice[0] == line[0]:
                    correct = "CORRECT"
                else:
                    correct = "WRONG"
                    wrong_counter += 1

            #correct = f"eric chose the {correct} function." if line[0] else "The input could not have yielded a correct answer" 
            out.insert(0, f"certainty: {certainty}")
            out.insert(0, correct)
            out.insert(0, f"{loading_bar} {datetime.now()}")
            out.append("=====================\n\n")

            out_all.extend(out)
            print(f"done{loading_bar}: {line}")
        #write everything at once
        wrong_percent = wrong_counter * 100.0 / length
        out_all.insert(0, f"wrong count: {wrong_counter}/{length} (~{wrong_percent}%)")
        list_to_file(out_all, output_file)
    print("---END---")
    
preface = [
    "PREPROCESSING:",
    "\tall lower case",
    "\tdelete punctuation",
    "\treplace placeholders in key_sentences with actual model-column-names from the input",
    "POSTPROCESSING:",
    "\tnone"

]

model_path = "data\\"
models = ["wiki.en.bin"]#, "wiki_bigrams.bin", "torontobooks_unigrams.bin", "wiki_unigrams.bin", "cc.en.300.bin"]
methods = ["minkowski"]#, "euclidean", "braycurtis", "chebyshev", "correlation", "cosine", "sqeuclidean"]

if False:
    for mod in models:
        print(f"loading {mod}")
        eric = eric_nlp.Eric_nlp(model_file = f"{model_path}{mod}")
        print(f"{mod} ready")
        for meth in methods:
            print(f"\tdoing {meth}")
            tester(meth, 50, eric, f"output\\vergleiche_umfrage\\{mod}_{meth}.txt")
else:
    umfragen = 4
    test_files = [f"data\\umfrage_input_{x}.txt" for x in range(1, umfragen+1)]
    for mod in models:
        print(f"loading {mod}")
        eric = eric_nlp.Eric_nlp(model_file = f"{model_path}{mod}")
        print(f"{mod} ready")
        for f in test_files:
            test_input = read_input_from_file(f)
            for meth in methods:
                print(f"\tdoing {mod}_{meth}_umfrage_{f[-5]}")
                tester(meth, 50, eric, f"output\\vergleiche_umfrage\\{mod}_{meth}_umfrage_{f[-5]}.txt")


'''
else:
    stanza.download("en")
    nlp = stanza.Pipeline(lang="en", processors="tokenize,mwt,pos,lemma,depparse")

    output = ["OUTPUT:\n"]
    for fct_id, sentence in test_input:
        doc = nlp(sentence)
        max_width_word = 0
        for word in sentence.split():
            width = len(word)
            if width > max_width_word:
                max_width_word = width

        append_data = []
        for sent in doc.sentences:
            sentence_words = ""
            root = ""
            for word in sent.words:
                if word.head == 0:
                    root = word.text
                append_data.append(f'id: {word.id}\tword: {word.text.ljust(max_width_word)}\tupos: {word.upos}\txpos: {word.xpos.ljust(3)}\thead id: {word.head}\thead: {sent.words[word.head-1].text.ljust(max_width_word) if word.head > 0 else "root".ljust(max_width_word)}\tdeprel: {word.deprel}')
                sentence_words += f"{word.text} "
            
            #console and txt-file output
            append_data.append("="*47 + "\n")
            output.append(sentence_words)
            output.append(f"Root: {root}")
            output.extend(append_data)

    for o in output:
        print(o)

quit()


'''




#OLD STUFF FROM DEPPARSING THAT MIGHT BE USED LATER
'''
def list_to_file(the_list, filename):
    with open(filename, "w") as f:
        for row in the_list:
            f.write(f"{row}\n")
    print(f"wrote list to {filename}")

output_path = "./output/"
#workbook = xls.Workbook(f"{output_path}output.xlsx")
#worksheet = workbook.add_worksheet("test_output")
out_file = f"{output_path}output.txt"
csv_out_file = f"{output_path}output.csv"
stanza.download("en")
nlp = stanza.Pipeline(lang="en", processors="tokenize,mwt,pos,lemma,depparse")
sentences = ["What can you predict for me?", "What if you change Age to 27?"]
test_data = ["Predict something.", "Predict something for me.", "Can you predict something for me?", "What if you try Z for X?", "What if you change X to Z?", "What if X was different?", "The professors love books.", "Books are loved by the professors.", "He reads Books.", "Books are read by him."]
# for d in dictionary:
#     test_data.append(d["display"])
#     test_data.append(d["write"])



print(test_data)
output = ["OUTPUT:"]
csv_output = ["OUTPUT:"]
for s in test_data:
    doc = nlp(s)
    max_width_word = 0
    for word in s.split():
        width = len(word)
        if width > max_width_word:
            max_width_word = width

    
    #sent are each a list of dicts (1 dict per word in the sentence)
    for sent in doc.sentences:
        append_data = []
        csv_append_data = ["ID;Word;uPOS;treePOS;Head ID;Head;DepRel"]
        sentence_words = ""
        root = ""
        for word in sent.words:
            if word.head == 0:
                root = word.text
            append_data.append(f'id: {word.id}\tword: {word.text.ljust(max_width_word)}\tupos: {word.upos}\txpos: {word.xpos.ljust(3)}\thead id: {word.head}\thead: {sent.words[word.head-1].text.ljust(max_width_word) if word.head > 0 else "root".ljust(max_width_word)}\tdeprel: {word.deprel}')
            csv_append_data.append(f'{word.id};{word.text};{word.upos};{word.xpos};{word.head};{sent.words[word.head-1].text if word.head > 0 else "root"};{word.deprel}')
            sentence_words += f"{word.text} "
        
        #console and txt-file output
        append_data.append("="*47 + "\n")
        output.append(sentence_words)
        output.append(f"Root: {root}")
        output.extend(append_data)
        #csv output
        csv_output.append("\n")
        csv_output.append(sentence_words)
        csv_output.append(f"Root: {root}")
        csv_output.extend(csv_append_data)

for o in output:
    print(o)
list_to_file(output, out_file)
list_to_file(csv_output, csv_out_file)


for s in sentences:
    tagged = nlp(s)
    print()
    print("="*17)
    print(tagged)
    print("-"*17)
    print(tagged.entities)

stanza.download("ja")
nlp_jp = stanza.Pipeline("ja")
tagged = nlp_jp("この花は特に春に美しく咲きます。")
print()
print("="*17)
print(tagged)
print("-"*17)
print(tagged.entities)
'''