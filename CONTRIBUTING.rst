Contributing
-----

We welcome contributions from the community to enhance Pykg2tbl. If you'd like to contribute, please follow these guidelines:

    1. Fork the repository and create a new branch for your feature or bug fix.
        1. `make init-dev` to install necessary development packages
    2. Make your changes and ensure that the code adheres to the project's coding style.
        1. `make fix-lint` will run the covention style formater.
        2. `make  check` will check if any aditional liting is necessary.
   Note: These steps are mandatory to merge, since the PR can only be merged if `make check` passes
    There is a pre-commit hook instaled with  init-dev that blocks commits unless they pass the lint check
    The commit  message also is checked in the hook, needing to adere to the `conventions<https://open-science.vliz.be/conventions.html>` 
    3. Write unit tests to cover your changes and ensure they pass.
   Note: A test coverage is also ensure, so new code must be also presented with the regarding unit test.
    4. Submit a pull request with a clear description of your changes and the problem they solve.


Thanks for joining us! Happy coding.