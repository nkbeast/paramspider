<h1 align="center">
    paramspider
  <br>
</h1>

<h4 align="center">  Mining URLs from dark corners of Web Archives for bug hunting/fuzzing/further probing </h4>

<p align="center">
  <a href="#about">📖 About</a> •
  <a href="#installation">🏗️ Installation</a> •
  <a href="#usage">⛏️ Usage</a> •
  <a href="#examples">🚀 Examples</a> •
  <a href="#contributing">🤝 Contributing</a> •
</p>


![paramspider](https://github.com/devanshbatham/ParamSpider/blob/master/static/paramspider.png?raw=true)

## About

`paramspider` allows you to fetch URLs related to any domain or a list of domains from Wayback achives. It filters out "boring" URLs, allowing you to focus on the ones that matter the most.

## Installation

To install `paramspider`, follow these steps:

```sh
git clone https://github.com/nkbeast/paramspider
```

## Usage

To use `paramspider`, follow these steps:

```sh
python3 paramspider.py -d example.com
```

## Examples

Here are a few examples of how to use `paramspider`:

- Discover URLs for a single domain:

  ```sh
  python3 paramspider.py -d example.com
  ```

- Discover URLs for multiple domains from a file:

  ```sh
  python3 paramspider.py -l domains.txt
  ```

- Stream URLs on the termial:

    ```sh 
    python3 paramspider.py -d example.com -s
    ```

- Set up web request proxy:

    ```sh
    python3 paramspider.py -d example.com --proxy '127.0.0.1:7890'
    ```
- Adding a placeholder for URL parameter values (default: "FUZZ"): 

  ```sh
   python3 paramspider.py -d example.com -p '"><h1>reflection</h1>'
  ```

