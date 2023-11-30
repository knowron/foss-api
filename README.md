<h3 align="center">
  <img width="400" src="https://user-images.githubusercontent.com/22967053/214530218-33fd1473-ff3d-4670-beb5-4a5d991d2ac6.png" alt="KNOWRON FOSS API">
</h3>

<br>

## 🗒️ Introduction

This repo defines a [serverless function](https://github.com/knowron/foss-api/blob/main/src/extraction.py) for PDF content extraction via [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/).

The function is currently implemented as an [AWS Lambda](https://aws.amazon.com/lambda/resources/) function deployed as a Docker container.

<br>

## 🏗️ Setting things up

<sup>Note: The following steps apply only to AWS.</sup>

First, the function has to be dockerized and pushed to [Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html). Thus, create an ECR repository and follow the steps displayed on the AWS Console when clicking on "View push commands" (replace `latest` by the appropriate version). With that, you'll have your Docker image built, pushed, and ready to be consumed by AWS Lambda.

Then, from AWS Lambda, set up a new function and specify the image pushed previously to ECR.

<br>

## 🔗 Dependencies

This project uses **[`pipenv`](https://pipenv.pypa.io/en/latest/index.html) to
handle dependencies.** Therefore, the only time you'll need to use `pip` should
be to install `pipenv` itself:

```console
pip install pipenv
```

<br>

Then, to **install the project dependencies**, simply run:

```console
pipenv install
```

<br>

#### 🤖 Other `pipenv` commands

To **install a Python module**, simply run:

```console
pipenv install package
```

or to **install a specific version**:

```console
pipenv install package==0.5
```

<br>

To **update all dependencies**:

```console
pipenv update
```

<br>

If you've updated any dependencies, **don't forget to recreate the `requirements.txt` file**:
```console
pipenv requirements > requirements.txt
```

<br>

To **activate the virtual environment**:

```console
pipenv shell
```

<br>

→ For more info and commands, please visit [`pipenv`
docs](https://pipenv.pypa.io/en/latest/index.html).

<br>

## ©️ Licensing

At KNOWRON, we take the recognition of FOSS projects seriously.

For any dependency you add, **don't forget** to include its license terms in
[`LICENSE`](https://github.com/knowron/foss-api/blob/main/LICENSE).
