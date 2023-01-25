<h3 align="center">
  <img width="400" src="https://user-images.githubusercontent.com/22967053/214530218-33fd1473-ff3d-4670-beb5-4a5d991d2ac6.png" alt="KNOWRON FOSS API">
</h3>

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
pipenv lock
```

<br>

→ For more info and commands, please visit [`pipenv`
docs](https://pipenv.pypa.io/en/latest/index.html).

<br>

## 🧨 Start up the server

First, place your `.env` under `src/`. To see which variables need to be
initialized see
[`src/env-example`](https://github.com/knowron/foss-api/blob/main/env-example).

<br>

Then, run:

```console
python run_local_server.py
```

<br>

Once you see:

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8002 (Press CTRL+C to quit)
```

you're ready to go!

<br>

## ©️ Licensing

At KNOWRON, we take the recognition of FOSS projects seriously.

For any dependency you add, **don't forget** to include its license terms in
[`LICENSE`](https://github.com/knowron/foss-api/blob/main/LICENSE).
