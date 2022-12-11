from nox_poetry import session

SRC = "pyqso"


@session(python=["3.10"])
def test(session):
    session.run(
        "pytest",
        "-vvv",
        "--cov-report=xml",
        "--cov=ioccheck",
        external=True,
    )


@session(python=["3.10"])
def lint(session):
    session.run("black", ".", external=True)
    session.run("flake8", SRC, "./test", external=True)
    session.run("bandit", "-r", SRC, external=True)
    session.run("mypy", "--warn-unreachable", SRC, external=True)
    session.run("pylint", SRC, external=True)
    session.run("isort", ".", external=True)


@session(python=["3.10"])
def docs(session):
    session.run(
        "sphinx-build", "-b", "html", "docs/source", "docs/build", external=True
    )
