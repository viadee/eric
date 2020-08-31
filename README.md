# ERIC conversational agent for XAI

![interface](/ERIC_interface.png)

ERIC is an acronym for "Explainable AI through Rule-based Interactive Conversation". ERIC applies different XAI methods to a machine learning model and uses the results to answer the questions that are asked by AI users in natural language. The method selection and the dialogue are supported by a rule-based expert system which consists of hand-crafted if-then-else rules. A potential user can communicate with ERIC through a chat-like conversational interface and receive appropriate explanations about the machine learning model’s reasoning behaviour. Since it is based on natural language understanding, the system is specifically targeted to domain experts who have an understanding of the data, but not about machine learning. ERIC is focused on classification tasks and tabular data sets.

Read more about it in this [article](http://ceur-ws.org/Vol-2578/ETMLP3.pdf).

## ERIC Extensions

ERIC is based on the rule-based programming language CLIPS that constructs the dialgue and performs XAI methods selection. However, ERIC can be extended by only using Python. ERIC extension objects will generate the rule logic automatically.

```python
def nthLargest(self, feature, nth):
    import pandas
    if feature in self.getContinuousFeatures():
        unique_values = self.X_train[feature].unique()
        unique_values.sort()
        return(str(unique_values[-1*nth]))
    else:
        return("NLargest cannot be calculated for categorical features.")

getNthLargest = ERICExtension(
    name = "getNLargest", 
    keywords = "nth largest large get",
    display = "What is the nth-largest value?",
    write = "What is the nth-largest value of feature Z?",
    description = "This command computes the nth-largest value for a given column.",
    output_type = "text", 
    arguments = {"feature": "Feature", "nth": "Integer"}, 
    function = nthLargest)
```

![interface](/ERIC_extension.png)

## Installation guide

### The current version of ERIC is an alpha release. Use at your own risk! ###

ERIC is a server-client application. 

The ERIC server runs with anaconda. You must first install anaconda. Then perform the following:

### Installation of the server (Windows):

    # create new conda env called eric from environment file
    conda env create -f environment_windows.yml
    # activate the conda env
    conda activate eric

Note: You must install wkhtmltopdf. To do so, download the latest version from https://wkhtmltopdf.org/downloads.html and run the installer. For Python to find the installation, you must add a path to the environment variable "path". Run:
    
    # add to env variable
    setx path "%path%;C:\Program Files\wkhtmltopdf\bin" 

### Installation of the server (OSX):

    # create new conda env called eric with necessary packages
    conda env create -f environment_osx.yml
    # activate the conda env
    conda activate eric

Note: For the clips expert system, there is a python implementation that must be installed (https://github.com/noxdafox/clipspy/). For Windows, clips is already installed in the previous step. For OSX you must install manually. However, there is a solution for this in https://github.com/noxdafox/clipspy/issues/18. 
<!--The required files that are used in the solution can be found in the clips-6.3.0 folder in the project folder. -->

You also must install wkhtmltopdf: For OSX this works via homebrew (https://brew.sh/index_de) by running:
    
    #install wkhtmltopdf
    brew cask install wkhtmltopdf

Independent form your OS, you must do the following (Windows and OSX):

    # fix a bug in graphviz
    dot -c

The following changes must be done to the installed packages within the anaconda environment. You find the packages in the directory where you installed anaconda:
* anaconda3⁩ ▸ ⁨envs⁩ ▸ eric ▸ ⁨lib⁩ ▸ ⁨(python3.7)⁩ ▸ ⁨(site-packages)⁩ ▸ ⁨ceteris_paribus⁩ ▸ ⁨plots⁩ ▸ plots.py: Line 156-165 replace with: "return(plot_id)"
<!-- * anaconda3⁩ ▸ ⁨envs⁩ ▸ eric ▸ ⁨lib⁩ ▸ ⁨python3.7⁩ ▸ ⁨(site-packages⁩) ▸ ⁨shap⁩ ▸ ⁨plots⁩ ▸ force_matplotlib.py: Line 149 replace with: "if True:"-->

Then you can the provided titanic example:
    
    # start the ERIC server
    python eric_titanic.py

### Installation of the client (Windows and OSX)

To install the client application you must do the following:
Since ReactJs is Javascript, you must install node.js (https://nodejs.org/en/download/). After node.js was installed, you can install ReactJs via the npm package manager that comes with node.js. Follow the instructions on https://www.npmjs.com/package/react and run:

    # install reactjs
    npm i react
 
After react was installed, cd into the client folder of the project. Run: 

    # install packages
    npm install
    # run the web dev server
    npm start

The client application should open http://localhost:3000/ in the browser. It will automatically connect to the server.

## Authors

* **Christian Werner** - *Initial work* - [Christian Werner](https://github.com/Bl7tzcrank)

## License

BSD 3-Clause License