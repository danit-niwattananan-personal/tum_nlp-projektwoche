## tum_nlp-projektwoche
### Setup
- First, install the `uv` Python package manager. Follow the official [uv documentation](https://docs.astral.sh/uv/getting-started/installation/) for installation instructions.
- `conda` might disrupt the environment during creation of `venv` of `uv`. Please deactivate conda and its environment variables before running `uv`, or purge it entirely.
- Clone the repository and, at the repo root, setup the dependencies with:
    ```
    uv sync
    ```
- For running `*.ipynb`, please also select the newly created `venv` as the kernel.

### Development
Please create another branch, commit and push your changes, and create pull request. Any issue can also be raised via the [issue tracker](https://github.com/danit-niwattananan-personal/tum_nlp-projektwoche/issues).