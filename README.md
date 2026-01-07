# vidyamitra-backend

# IDE
Download VS Code IDE 
[VS Code](https://code.visualstudio.com/download)


# Download (Programing Language)
[Python-version-3.12.4](https://www.python.org/downloads/)


[Django-verion-5.0.7](https://www.djangoproject.com/download/)



# Download Software

[Github](https://desktop.github.com/download/)


[Git](https://git-scm.com/downloads)



## Make a account on Below these to retrive API Keys

[Pinecone](https://www.pinecone.io/)


[Gooogle AI Studio](https://ai.google.dev/aistudio) 


[OpenAI](https://openai.com/)




# Project Setup

## Prerequisites

###  WSL installation

Open PowerShell or Windows Command Prompt in **administrator** mode by right-clicking and selecting "Run as administrator", enter the wsl --install command, then restart your machine.

    wsl --install

This command will enable the features necessary to run WSL and install the Ubuntu distribution of Linux.




### SSH keys setup 


Follow the detailed instructions here to setup ssh keys for your github account: 
[SSH keys setup](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

### Install dependencies 

    sudo apt update && sudo apt upgrade
    sudo apt install build-essential libssl-dev zlib1g-dev \ libbz2-dev libreadline-dev libsqlite3-dev curl git \ libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev


 
## Clone vidyamitra

**Clone the repo:** 

```
git clone "git@github.com:REVA-git/vidyamitra.git"
```
    cd vidyamitra
**Open the vscode workspace file**

    code vidyamitra.code-workspace

**Navigate to the backend folder:** 
    
    cd vidyamitra/backend

## Download and install dependencies


### Automatic installer

```
bash setup.sh
```
Reload the shell.

```
source ~/.bashrc
```

> :warning: If there is any error while installing you can follow the mannual procedure.

### Mannual Installation

**Install pyenv**

    curl [https://pyenv.run](https://pyenv.run/) | bash

**Add path:**

```
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc 
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc 
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
```

**Install python 3.12 :**

    pyenv install 3.12

**Set to global version:**

    penv global 3.12


## Poetry installation 

Poetry is a tool for **dependency management** and **packaging** in Python. Poetry offers a lockfile to ensure repeatable installs, and can build your project for distribution.


*Try:*

    pipx install poetry


or, 

    pip install poetry



Now install pants,


    curl --proto '=https' --tlsv1.2 -fsSL https://static.pantsbuild.org/setup/get-pants.sh | bash
    
Include the local installation directory if not done. 

    echo 'PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    
    source ~/.bashrc


**Install dependencies using poetry:** 

    poetry install

**Intialise pants:**

    pants


## API keys setup: 

Navigate to backend dir :

    cd backend

Create a new file inside backend folder and name it ".env" 
Add the respective api keys. 

    GOOGLE_API_KEY=""
    PINECONE_INDEX_NAME = ""
    PINECONE_API_KEY = ""
    OPENAI_API_KEY = ""
    OPENAI_ORGANIZATION = ""
    BACKEND_HOST="[http://localhost:8000/"](http://localhost:8000/%22 "http://localhost:8000/%22")
    GENERATED_SLIDES_FOLDER="slides/generated/"
    TEMPLATE_FOLDER="slides/template/base.pptx"
