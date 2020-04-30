import eric_nlp
import time
from datetime import datetime
input_from_console = False
output_path = "output\\"
output_file = "method_comparison.txt"
test_input = [
    "Hello",
    "Please make a prediction.",
    "prediction",
    "Would you predict something for me?",
    "What if you changed Sex to Male?",
    "What if Age was 24?",
    "What if age 33",
    "can you show me what you use as input?",
    "do you have any samples?",
    "what if age was greater?",
    "what if relatives was different?",
    "When do you change your prediction?",
    "What are your parameters?",
    #input with unacceptable parameters
    "What if Relatives was 999",
    "What if Age was -3.6?",
    #nonsense input
    "I want to eat some sandwiches!",
    "You want to eat some sandwiches!",
    "The earth is actually flat",
    "These aren't the droids you are looking for.",
    "Belinda blinked, it wasn't a dream."
]


def list_to_file(the_list, filename, mode="w"):
    with open(filename, mode) as f:
        for row in the_list:
            f.write(f"{row}\n")
    print(f"wrote list to {filename}")


def tester(method, limit, comment=["No comment given", "Make sense of it on your own", "Text speaks for itself"]):
    print("loading model")
    eric = eric_nlp.Eric_nlp()
    print("model ready")
    out_all = [
        f"Every entry shows a timestamp, then the input sentence and the top {limit} matches that were found (if that many exist).",
        "entries sorted by <CALCULATED>. The other column headline in <> is the algorithm that was used.",
        "\n",
        "//// BEGIN Test comments: ////"
    ]
    out_all.extend(comment)
    out_all.append("//// END Test comments: ////\n")

    out = ["no output exists"]
    file_name = output_path + output_file
    
    print("---START---")
    if input_from_console:
        input_counter = 1
        while True:
            usr_in = input()
            if usr_in == "exit":
                break
            out = eric.method_comparison(usr_in, method=method, limit=limit)
            out.insert(0, f"{input_counter}: {datetime.now()}")
            input_counter += 1
            out.append("=====================\n\n")
            #extend file every time
            out_all.extend(out)
            for o in out:
                print(o)
            list_to_file(out_all, file_name)
    else:
        length = len(test_input)
        for line, index in zip(test_input, range(length)):
            #cosmetic
            loading_bar = f"({index+1}/{length})"

            out = eric.method_comparison(line, method=method, limit=limit)
            out.insert(0, f"{loading_bar} {datetime.now()}")
            out.append("=====================\n\n")

            out_all.extend(out)
            print(f"done{loading_bar}: {line}")
        #write everything at once
        list_to_file(out_all, file_name)
    print("---END---")
    
preface = [
    "PREPROCESSING:",
    "\tall lower case",
    "\tdelete punctuation",
    "\treplace placeholders in key_sentences with actual model-column-names from the input",
    "POSTPROCESSING:",
    "\tnone"

]
tester("cosine", 99, comment=preface)



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