# mini-rag
from mini rag course on youtub https://www.youtube.com/watch?v=VSFbkFRAT4w&amp;list=PLvLvlVqNQGHCUR2p0b8a0QpVjDUg50wQj&amp;index=3

this is a minimal implementation of the RAG model for question
answering.

## Requirements

- Python 3.8 or later

#### Install Python using Miniconda

1) Download and install MiniConda from [here](https://www.anaconda.com/docs/getting-started/miniconda/install#linux-terminal-installer)
2) Create a new environment using the following command:
```bash
$ conda create -n mini-rag python3.8
```
3) Activate the environment:
```bash
$ conda activate mini-rag
```
### (optional) Setup your command line for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt 
```

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your environment variables in the '.env' file. Like 'OPENAI_API_KEY'
