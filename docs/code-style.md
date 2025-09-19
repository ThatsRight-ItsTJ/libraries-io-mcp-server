
# Code Style Guidelines

This document provides comprehensive guidelines for code style and formatting in the Libraries.io MCP Server project. Following these guidelines ensures consistent, readable, and maintainable code across the entire codebase.

## Overview

The Libraries.io MCP Server follows Python PEP 8 standards with additional project-specific conventions. The code style is enforced using automated tools to maintain consistency across the codebase.

## Core Tools

### 1. Black - Code Formatting

Black is the primary code formatter for the project. It enforces a consistent code style automatically.

#### Installation

```bash
pip install black
```

#### Usage

```bash
# Format all Python files
black src/

# Format specific file
black src/libraries_io_mcp/client.py

# Check formatting without making changes
black --check src/

# Diff mode to see what would change
black --diff src/
```

#### Black Configuration

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

### 2. isort - Import Sorting

isort sorts Python imports according to PEP 8 and project conventions.

#### Installation

```bash
pip install isort
```

#### Usage

```bash
# Sort imports in all Python files
isort src/

# Sort imports in specific file
isort src/libraries_io_mcp/client.py

# Check sorting without making changes
isort --check-only src/

# Diff mode to see what would change
isort --diff src/
```

#### isort Configuration

```toml
# pyproject.toml
[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88
known_first_party = ["libraries_io_mcp"]
```

### 3. flake8 - Linting

flake8 checks for style errors, syntax errors, and undefined names.

#### Installation

```bash
pip install flake8
```

#### Usage

```bash
# Lint all Python files
flake8 src/

# Lint specific file
flake8 src/libraries_io_mcp/client.py

# Show line numbers
flake8 --show-source src/

# Show statistics
flake8 --statistics src/
```

#### flake8 Configuration

```toml
# pyproject.toml
[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]
exclude = [
    ".git",
    "__pycache__",
    "build",
    "dist",
    ".eggs",
    "*.egg-info",
    ".tox",
    ".venv",
]
per-file-ignores = [
    "tests/*:E501,W503",
    "*/__init__.py:F401",
]
```

### 4. mypy - Type Checking

mypy performs static type checking on Python code.

#### Installation

```bash
pip install mypy
```

#### Usage

```bash
# Type check all Python files
mypy src/

# Type check specific file
mypy src/libraries_io_mcp/client.py

# Show line numbers
mypy --show-line-numbers src/

# Show error codes
mypy --show-error-codes src/
```

#### mypy Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
show_error_codes = true
show_error_context = true
pretty = true
show_column_numbers = true
ignore_missing_imports = true
implicit_reexport = false
strict_optional = true
warn_unused_configs = true
warn_unused_ignores = true
warn_no_return = true
warn_redundant_casts = true
warn_unreachable = true
strict_equality = true
show_error_codes = true
show_error_context = true
pretty = true
show_column_numbers = true

[[tool.mypy.overrides]]
module = [
    "tests.*",
    "test_utils.*",
    "conftest.*",
]
ignore_errors = true
```

### 5. ruff - Alternative Linter

ruff is a fast Python linter written in Rust that can replace flake8, isort, and some pyupgrade functionality.

#### Installation

```bash
pip install ruff
```

#### Usage

```bash
# Lint all Python files
ruff check src/

# Fix auto-fixable issues
ruff check --fix src/

# Format imports
ruff format src/

# Check specific rules
ruff check --select E,W,F,I src/

# Exclude specific files
ruff check --exclude tests src/
```

#### ruff Configuration

```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py38"
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "C",  # flake8-comprehensions
    "B",  # flake8-bugbear
    "S",  # flake8-bandit
    "T",  # flake8-print
    "UP", # pyupgrade
    "RUF", # ruff-specific rules
]
ignore = [
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
    "S101",  # use of assert
    "S603",  # subprocess call: check for execution of untrusted input
    "S607",  # starting a process with a partial executable path
]
exclude = [
    ".bzr",
    ".direnv",
    ".eggs",
    ".git",
    ".git-rewrite",
    ".hg",
    ".mypy_cache",
    ".nox",
    ".pants.d",
    ".pytype",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "__pypackages__",
    "_build",
    "build",
    "dist",
    "node_modules",
    "venv",
]

[tool.ruff.per-file-ignores]
"tests/*" = [
    "S101",  # allow asserts in tests
    "S106",  # allow hard-coded passwords in tests
    "S108",  # allow temporary file creation in tests
    "S311",  # allow pseudo-random number generators in tests
    "S603",  # allow subprocess calls in tests
    "S607",  # allow partial executable paths in tests
    "ARG001", # allow unused arguments in test functions
    "ARG002", # allow unused arguments in test functions
    "ARG003", # allow unused arguments in test functions
    "ARG004", # allow unused arguments in test functions
    "ARG005", # allow unused arguments in test functions
    "PLR0913", # allow too many arguments in test functions
    "PLR0915", # allow too many statements in test functions
    "PLR2004", # allow magic numbers in tests
    "PLW0603", # allow global statements in tests
    "PLW2901", # allow allow-loop variable overwrite in tests
    "PT011",  # allow pytest.raises without match parameter
    "PT012",  # allow pytest.raises with broad exception
    "PT013",  # allow pytest.raises with wrong exception type
    "PT017",  # allow pytest.raises with too broad exception
    "PT018",  # allow pytest.raises with wrong exception type
    "PT019",  # allow pytest.raises with wrong exception type
    "PT020",  # allow pytest.raises with wrong exception type
    "PT021",  # allow pytest.raises with wrong exception type
    "PT022",  # allow pytest.raises with wrong exception type
    "PT023",  # allow pytest.raises with wrong exception type
    "PT024",  # allow pytest.raises with wrong exception type
    "PT025",  # allow pytest.raises with wrong exception type
    "PT026",  # allow pytest.raises with wrong exception type
    "PT027",  # allow pytest.raises with wrong exception type
    "PT028",  # allow pytest.raises with wrong exception type
    "PT029",  # allow pytest.raises with wrong exception type
    "PT030",  # allow pytest.raises with wrong exception type
    "PT031",  # allow pytest.raises with wrong exception type
    "PT032",  # allow pytest.raises with wrong exception type
    "PT033",  # allow pytest.raises with wrong exception type
    "PT034",  # allow pytest.raises with wrong exception type
    "PT035",  # allow pytest.raises with wrong exception type
    "PT036",  # allow pytest.raises with wrong exception type
    "PT037",  # allow pytest.raises with wrong exception type
    "PT038",  # allow pytest.raises with wrong exception type
    "PT039",  # allow pytest.raises with wrong exception type
    "PT040",  # allow pytest.raises with wrong exception type
    "PT041",  # allow pytest.raises with wrong exception type
    "PT042",  # allow pytest.raises with wrong exception type
    "PT043",  # allow pytest.raises with wrong exception type
    "PT044",  # allow pytest.raises with wrong exception type
    "PT045",  # allow pytest.raises with wrong exception type
    "PT046",  # allow pytest.raises with wrong exception type
    "PT047",  # allow pytest.raises with wrong exception type
    "PT048",  # allow pytest.raises with wrong exception type
    "PT049",  # allow pytest.raises with wrong exception type
    "PT050",  # allow pytest.raises with wrong exception type
    "PT051",  # allow pytest.raises with wrong exception type
    "PT052",  # allow pytest.raises with wrong exception type
    "PT053",  # allow pytest.raises with wrong exception type
    "PT054",  # allow pytest.raises with wrong exception type
    "PT055",  # allow pytest.raises with wrong exception type
    "PT056",  # allow pytest.raises with wrong exception type
    "PT057",  # allow pytest.raises with wrong exception type
    "PT058",  # allow pytest.raises with wrong exception type
    "PT059",  # allow pytest.raises with wrong exception type
    "PT060",  # allow pytest.raises with wrong exception type
    "PT061",  # allow pytest.raises with wrong exception type
    "PT062",  # allow pytest.raises with wrong exception type
    "PT063",  # allow pytest.raises with wrong exception type
    "PT064",  # allow pytest.raises with wrong exception type
    "PT065",  # allow pytest.raises with wrong exception type
    "PT066",  # allow pytest.raises with wrong exception type
    "PT067",  # allow pytest.raises with wrong exception type
    "PT068",  # allow pytest.raises with wrong exception type
    "PT069",  # allow pytest.raises with wrong exception type
    "PT070",  # allow pytest.raises with wrong exception type
    "PT071",  # allow pytest.raises with wrong exception type
    "PT072",  # allow pytest.raises with wrong exception type
    "PT073",  # allow pytest.raises with wrong exception type
    "PT074",  # allow pytest.raises with wrong exception type
    "PT075",  # allow pytest.raises with wrong exception type
    "PT076",  # allow pytest.raises with wrong exception type
    "PT077",  # allow pytest.raises with wrong exception type
    "PT078",  # allow pytest.raises with wrong exception type
    "PT079",  # allow pytest.raises with wrong exception type
    "PT080",  # allow pytest.raises with wrong exception type
    "PT081",  # allow pytest.raises with wrong exception type
    "PT082",  # allow pytest.raises with wrong exception type
    "PT083",  # allow pytest.raises with wrong exception type
    "PT084",  # allow pytest.raises with wrong exception type
    "PT085",  # allow pytest.raises with wrong exception type
    "PT086",  # allow pytest.raises with wrong exception type
    "PT087",  # allow pytest.raises with wrong exception type
    "PT088",  # allow pytest.raises with wrong exception type
    "PT089",  # allow pytest.raises with wrong exception type
    "PT090",  # allow pytest.raises with wrong exception type
    "PT091",  # allow pytest.raises with wrong exception type
    "PT092",  # allow pytest.raises with wrong exception type
    "PT093",  # allow pytest.raises with wrong exception type
    "PT094",  # allow pytest.raises with wrong exception type
    "PT095",  # allow pytest.raises with wrong exception type
    "PT096",  # allow pytest.raises with wrong exception type
    "PT097",  # allow pytest.raises with wrong exception type
    "PT098",  # allow pytest.raises with wrong exception type
    "PT099",  # allow pytest.raises with wrong exception type
    "PT100",  # allow pytest.raises with wrong exception type
    "PT101",  # allow pytest.raises with wrong exception type
    "PT102",  # allow pytest.raises with wrong exception type
    "PT103",  # allow pytest.raises with wrong exception type
    "PT104",  # allow pytest.raises with wrong exception type
    "PT105",  # allow pytest.raises with wrong exception type
    "PT106",  # allow pytest.raises with wrong exception type
    "PT107",  # allow pytest.raises with wrong exception type
    "PT108",  # allow pytest.raises with wrong exception type
    "PT109",  # allow pytest.raises with wrong exception type
    "PT110",  # allow pytest.raises with wrong exception type
    "PT111",  # allow pytest.raises with wrong exception type
    "PT112",  # allow pytest.raises with wrong exception type
    "PT113",  # allow pytest.raises with wrong exception type
    "PT114",  # allow pytest.raises with wrong exception type
    "PT115",  # allow pytest.raises with wrong exception type
    "PT116",  # allow pytest.raises with wrong exception type
    "PT117",  # allow pytest.raises with wrong exception type
    "PT118",  # allow pytest.raises with wrong exception type
    "PT119",  # allow pytest.raises with wrong exception type
    "PT120",  # allow pytest.raises with wrong exception type
    "PT121",  # allow pytest.raises with wrong exception type
    "PT122",  # allow pytest.raises with wrong exception type
    "PT123",  # allow pytest.raises with wrong exception type
    "PT124",  # allow pytest.raises with wrong exception type
    "PT125",  # allow pytest.raises with wrong exception type
    "PT126",  # allow pytest.raises with wrong exception type
    "PT127",  # allow pytest.raises with wrong exception type
    "PT128",  # allow pytest.raises with wrong exception type
    "PT129",  # allow pytest.raises with wrong exception type
    "PT130",  # allow pytest.raises with wrong exception type
    "PT131",  # allow pytest.raises with wrong exception type
    "PT132",  # allow pytest.raises with wrong exception type
    "PT133",  # allow pytest.raises with wrong exception type
    "PT134",  # allow pytest.raises with wrong exception type
    "PT135",  # allow pytest.raises with wrong exception type
    "PT136",  # allow pytest.raises with wrong exception type
    "PT137",  # allow pytest.raises with wrong exception type
    "PT138",  # allow pytest.raises with wrong exception type
    "PT139",  # allow pytest.raises with wrong exception type
    "PT140",  # allow pytest.raises with wrong exception type
    "PT141",  # allow pytest.raises with wrong exception type
    "PT142",  # allow pytest.raises with wrong exception type
    "PT143",  # allow pytest.raises with wrong exception type
    "PT144",  # allow pytest.raises with wrong exception type
    "PT145",  # allow pytest.raises with wrong exception type
    "PT146",  # allow pytest.raises with wrong exception type
    "PT147",  # allow pytest.raises with wrong exception type
    "PT148",  # allow pytest.raises with wrong exception type
    "PT149",  # allow pytest.raises with wrong exception type
    "PT150",  # allow pytest.raises with wrong exception type
    "PT151",  # allow pytest.raises with wrong exception type
    "PT152",  # allow pytest.raises with wrong exception type
    "PT153",  # allow pytest.raises with wrong exception type
    "PT154",  # allow pytest.raises with wrong exception type
    "PT155",  # allow pytest.raises with wrong exception type
    "PT156",  # allow pytest.raises with wrong exception type
    "PT157",  # allow pytest.raises with wrong exception type
    "PT158",  # allow pytest.raises with wrong exception type
    "PT159",  # allow pytest.raises with wrong exception type
    "PT160",  # allow pytest.raises with wrong exception type
    "PT161",  # allow pytest.raises with wrong exception type
    "PT162",  # allow pytest.raises with wrong exception type
    "PT163",  # allow pytest.raises with wrong exception type
    "PT164",  # allow pytest.raises with wrong exception type
    "PT165",  # allow pytest.raises with wrong exception type
    "PT166",  # allow pytest.raises with wrong exception type
    "PT167",  # allow pytest.raises with wrong exception type
    "PT168",  # allow pytest.raises with wrong exception type
    "PT169",  # allow pytest.raises with wrong exception type
    "PT170",  # allow pytest.raises with wrong exception type
    "PT171",  # allow pytest.raises with wrong exception type
    "PT172",  # allow pytest.raises with wrong exception type
    "PT173",  # allow pytest.raises with wrong exception type
    "PT174",  # allow pytest.raises with wrong exception type
    "PT175",  # allow pytest.raises with wrong exception type
    "PT176",  # allow pytest.raises with wrong exception type
    "PT177",  # allow pytest.raises with wrong exception type
    "PT178",  # allow pytest.raises with wrong exception type
    "PT179",  # allow pytest.raises with wrong exception type
    "PT180",  # allow pytest.raises with wrong exception type
    "PT181",  # allow pytest.raises with wrong exception type
    "PT182",  # allow pytest.raises with wrong exception type
    "PT183",  # allow pytest.raises with wrong exception type
    "PT184",  # allow pytest.raises with wrong exception type
    "PT185",  # allow pytest.raises with wrong exception type
    "PT186",  # allow pytest.raises with wrong exception type
    "PT187",  # allow pytest.raises with wrong exception type
    "PT188",  # allow pytest.raises with wrong exception type
    "PT189",  # allow pytest.raises with wrong exception type
    "PT190",  # allow pytest.raises with wrong exception type
    "PT191",  # allow pytest.raises with wrong exception type
    "PT192",  # allow pytest.raises with wrong exception type
    "PT193",  # allow pytest.raises with wrong exception type
    "PT194",  # allow pytest.raises with wrong exception type
    "PT195",  # allow pytest.raises with wrong exception type
    "PT196",  # allow pytest.raises with wrong exception type
    "PT197",  # allow pytest.raises with wrong exception type
    "PT198",  # allow pytest.raises with wrong exception type
    "PT199",  # allow pytest.raises with wrong exception type
    "PT200",  # allow pytest.raises with wrong exception type
    "PT201",  # allow pytest.raises with wrong exception type
    "PT202",  # allow pytest.raises with wrong exception type
    "PT203",  # allow pytest.raises with wrong exception type
    "PT204",  # allow pytest.raises with wrong exception type
    "PT205",  # allow pytest.raises with wrong exception type
    "PT206",  # allow pytest.raises with wrong exception type
    "PT207",  # allow pytest.raises with wrong exception type
    "PT208",  # allow pytest.raises with wrong exception type
    "PT209",  # allow pytest.raises with wrong exception type
    "PT210",  # allow pytest.raises with wrong exception type
    "PT211",  # allow pytest.raises with wrong exception type
    "PT212",  # allow pytest.raises with wrong exception type
    "PT213",  # allow pytest.raises with wrong exception type
    "PT214",  # allow pytest.raises with wrong exception type
    "PT215",  # allow pytest.raises with wrong exception type
    "PT216",  # allow pytest.raises with wrong exception type
    "PT217",  # allow pytest.raises with wrong exception type
    "PT218",  # allow pytest.raises with wrong exception type
    "PT219",  # allow pytest.raises with wrong exception type
    "PT220",  # allow pytest.raises with wrong exception type
    "PT221",  # allow pytest.raises with wrong exception type
    "PT222",  # allow pytest.raises with wrong exception type
    "PT223",  # allow pytest.raises with wrong exception type
    "PT224",  # allow pytest.raises with wrong exception type
    "PT225",  # allow pytest.raises with wrong exception type
    "PT226",  # allow pytest.raises with wrong exception type
    "PT227",  # allow pytest.raises with wrong exception type
    "PT228",  # allow pytest.raises with wrong exception type
    "PT229",  # allow pytest.raises with wrong exception type
    "PT230",  # allow pytest.raises with wrong exception type
    "PT231",  # allow pytest.raises with wrong exception type
    "PT232",  # allow pytest.raises with wrong exception type
    "PT233",  # allow pytest.raises with wrong exception type
    "PT234",  # allow pytest.raises with wrong exception type
    "PT235",  # allow pytest.raises with wrong exception type
    "PT236",  # allow pytest.raises with wrong exception type
    "PT237",  # allow pytest.raises with wrong exception type
    "PT238",  # allow pytest.raises with wrong exception type
    "PT239",  # allow pytest.raises with wrong exception type
    "PT240",  # allow pytest.raises with wrong exception type
    "PT241",  # allow pytest.raises with wrong exception type
    "PT242",  # allow pytest.raises with wrong exception type
    "PT243",  # allow pytest.raises with wrong exception type
    "PT244",  # allow pytest.raises with wrong exception type
    "PT245",  # allow pytest.raises with wrong exception type
    "PT246",  # allow pytest.raises with wrong exception type
    "PT247",  # allow pytest.raises with wrong exception type
    "PT248",  # allow pytest.raises with wrong exception type
    "PT249",  # allow pytest.raises with wrong exception type
    "PT250",  # allow pytest.raises with wrong exception type
    "PT251",  # allow pytest.raises with wrong exception type
    "PT252",  # allow pytest.raises with wrong exception type
    "PT253",  # allow pytest.raises with wrong exception type
    "PT254",  # allow pytest.raises with wrong exception type
    "PT255",  # allow pytest.raises with wrong exception type
    "PT256",  # allow pytest.raises with wrong exception type
    "PT257",  # allow pytest.raises with wrong exception type
    "PT258",  # allow pytest.raises with wrong exception type
    "PT259",  # allow pytest.raises with wrong exception type
    "PT260",  # allow pytest.raises with wrong exception type
    "PT261",  # allow pytest.raises with wrong exception type
    "PT262",  # allow pytest.raises with wrong exception type
    "PT263",  # allow pytest.raises with wrong exception type
    "PT264",  # allow pytest.raises with wrong exception type
    "PT265",  # allow pytest.raises with wrong exception type
    "PT266",  # allow pytest.raises with wrong exception type
    "PT267",  # allow pytest.raises with wrong exception type
    "PT268",  # allow pytest.raises with wrong exception type
    "PT269",  # allow pytest.raises with wrong exception type
    "PT270",  # allow pytest.raises with wrong exception type
    "PT271",  # allow pytest.raises with wrong exception type
    "PT272",  # allow pytest.raises with wrong exception type
    "PT273",  # allow pytest.raises with wrong exception type
    "PT274",  # allow pytest.raises with wrong exception type
    "PT275",  # allow pytest.raises with wrong exception type
    "PT276",  # allow pytest.raises with wrong exception type
    "PT277",  # allow pytest.raises with wrong exception type
    "PT278",  # allow pytest.raises with wrong exception type
    "PT279",  # allow pytest.raises with wrong exception type
    "PT280",  # allow pytest.raises with wrong exception type
    "PT281",  # allow pytest.raises with wrong exception type
    "PT282",  # allow pytest.raises with wrong exception type
    "PT283",  # allow pytest.raises with wrong exception type
    "PT284",  # allow pytest.raises with wrong exception type
    "PT285",  # allow pytest.raises with wrong exception type
    "PT286",  # allow pytest.raises with wrong exception type
    "PT287",  # allow pytest.raises with wrong exception type
    "PT288",  # allow pytest.raises with wrong exception type
    "PT289",  # allow pytest.raises with wrong exception type
    "PT290",  # allow pytest.raises with wrong exception type
    "PT291",  # allow pytest.raises with wrong exception type
    "PT292",  # allow pytest.raises with wrong exception type
    "PT293",  # allow pytest.raises with wrong exception type
    "PT294",  # allow pytest.raises with wrong exception type
    "PT295",  # allow pytest.raises with wrong exception type
    "PT296",  # allow pytest.raises with wrong exception type
    "PT297",  # allow pytest.raises with wrong exception type
    "PT298",  # allow pytest.raises with wrong exception type
    "PT299",  # allow pytest.raises with wrong exception type
    "PT300",  # allow pytest.raises with wrong exception type
    "PT301",  # allow pytest.raises with wrong exception type
    "PT302",  # allow pytest.raises with wrong exception type
    "PT303",  # allow pytest.raises with wrong exception type
    "PT304",  # allow pytest.raises with wrong exception type
    "PT305",  # allow pytest.raises with wrong exception type
    "PT306",  # allow pytest.raises with wrong exception type
    "PT307",  # allow pytest.raises with wrong exception type
    "PT308",  # allow pytest.raises with wrong exception type
    "PT309",  # allow pytest.raises with wrong exception type
    "PT310",  # allow pytest.raises with wrong exception type
    "PT311",  # allow pytest.raises with wrong exception type
    "PT312",  # allow pytest.raises with wrong exception type
    "PT313",  # allow pytest.raises with wrong exception type
    "PT314",  # allow pytest.raises with wrong exception type
    "PT315",  # allow pytest.raises with wrong exception type
    "PT316",  # allow pytest.raises with wrong exception type
    "PT317",  # allow pytest.raises with wrong exception type
    "PT318",  # allow pytest.raises with wrong exception type
    "PT319",  # allow pytest.raises with wrong exception type
    "PT320",  # allow pytest.raises with wrong exception type
    "PT321",  # allow pytest.raises with wrong exception type
    "PT322",  # allow pytest.raises with wrong exception type
    "PT323",  # allow pytest.raises with wrong exception type
    "PT324",  # allow pytest.raises with wrong exception type
    "PT325",  # allow pytest.raises with wrong exception type
    "PT326",  # allow pytest.raises with wrong exception type
    "PT327",  # allow pytest.raises with wrong exception type
    "PT328",  # allow pytest.raises with wrong exception type
    "PT329",  # allow pytest.raises with wrong exception type
    "PT330",  # allow pytest.raises with wrong exception type
    "PT331",  # allow pytest.raises with wrong exception type
    "PT332",  # allow pytest.raises with wrong exception type
    "PT333",  # allow pytest.raises with wrong exception type
    "PT334",  # allow pytest.raises with wrong exception type
    "PT335",  # allow pytest.raises with wrong exception type
    "PT336",  # allow pytest.raises with wrong exception type
    "PT337",  # allow pytest.raises with wrong exception type
    "PT338",  # allow pytest.raises with wrong exception type
    "PT339",  # allow pytest.raises with wrong exception type
    "PT340",  # allow pytest.raises with wrong exception type
    "PT341",  # allow pytest.raises with wrong exception type
    "PT342",  # allow pytest.raises with wrong exception type
    "PT343",  # allow pytest.raises with wrong exception type
    "PT344",  # allow pytest.raises with wrong exception type
    "PT345",  # allow pytest.raises with wrong exception type
    "PT346",  # allow pytest.raises with wrong exception type
    "PT347",  # allow pytest.raises with wrong exception type
    "PT348",  # allow pytest.raises with wrong exception type
    "PT349",  # allow pytest.raises with wrong exception type
    "PT350",  # allow pytest.raises with wrong exception type
    "PT351",  # allow pytest.raises with wrong exception type
    "PT352",  # allow pytest.raises with wrong exception type
    "PT353",  # allow pytest.raises with wrong exception type
    "PT354",  # allow pytest.raises with wrong exception type
    "PT355",  # allow pytest.raises with wrong exception type
    "PT356",  # allow pytest.raises with wrong exception type
    "PT357",  # allow pytest.raises with wrong exception type
    "PT358",  # allow pytest.raises with wrong exception type
    "PT359",  # allow pytest.raises with wrong exception type
    "PT360",  # allow pytest.raises with wrong exception type
    "PT361",  # allow pytest.raises with wrong exception type
    "PT362",  # allow pytest.raises with wrong exception type
    "PT363",  # allow pytest.raises with wrong exception type
    "PT364",  # allow pytest.raises with wrong exception type
    "PT365",  # allow pytest.raises with wrong exception type
    "PT366",  # allow pytest.raises with wrong exception type
    "PT367",  # allow pytest.raises with wrong exception type
    "PT368",  # allow pytest.raises with wrong exception type
    "PT369",  # allow pytest.raises with wrong exception type
    "PT370",  # allow pytest.raises with wrong exception type
    "PT371",  # allow pytest.raises with wrong exception type
    "PT372",  # allow pytest.raises with wrong exception type
    "PT373",  # allow pytest.raises with wrong exception type
    "PT374",  # allow pytest.raises with wrong exception type
    "PT375",  # allow pytest.raises with wrong exception type
    "PT376",  # allow pytest.raises with wrong exception type
    "PT377",  # allow pytest.raises with wrong exception type
    "PT378",  # allow pytest.raises with wrong exception type
    "PT379",  # allow pytest.raises with wrong exception type
    "PT380",  # allow pytest.raises with wrong exception type
    "PT381",  # allow pytest.raises with wrong exception type
    "PT382",  # allow pytest.raises with wrong exception type
    "PT383",  # allow pytest.raises with wrong exception type
    "PT384",  # allow pytest.raises with wrong exception type
    "PT385",  # allow pytest.raises with wrong exception type
    "PT386",  # allow pytest.raises with wrong exception type
    "PT387",  # allow pytest.raises with wrong exception type
    "PT388",  # allow pytest.raises with wrong exception type
    "PT389",  # allow pytest.raises with wrong exception type
    "PT390",  # allow pytest.raises with wrong exception type
    "PT391",  # allow pytest.raises with wrong exception type
    "PT392",  # allow pytest.raises with wrong exception type
    "PT393",  # allow pytest.raises with wrong exception type
    "PT394",  # allow pytest.raises with wrong exception type
    "PT395",  # allow pytest.raises with wrong exception type
    "PT396",  # allow pytest.raises with wrong exception type
    "PT397",  # allow pytest.raises with wrong exception type
    "PT398",  # allow pytest.raises with wrong exception type
    "PT399",  # allow pytest.raises with wrong exception type
    "PT400",  # allow pytest.raises with wrong exception type
    "PT401",  # allow pytest.raises with wrong exception type
    "PT402",  # allow pytest.raises with wrong exception type
    "PT403",  # allow pytest.raises with wrong exception type
    "PT404",  # allow pytest.raises with wrong exception type
    "PT405",  # allow pytest.raises with wrong exception type
    "PT406",  # allow pytest.raises with wrong exception type
    "PT407",  # allow pytest.raises with wrong exception type
    "PT408",  # allow pytest.raises with wrong exception type
    "PT409",  # allow pytest.raises with wrong exception type
    "PT410",  # allow pytest.raises with wrong exception type
    "PT411",  # allow pytest.raises with wrong exception type
    "PT412",  # allow pytest.raises with wrong exception type
    "PT413",  # allow pytest.raises with wrong exception type
    "PT414",  # allow pytest.raises with wrong exception type
    "PT415",  # allow pytest.raises with wrong exception type
    "PT416",  # allow pytest.raises with wrong exception type
    "PT417",  # allow pytest.raises with wrong exception type
    "PT418",  # allow pytest.raises with wrong exception type
    "PT419",  # allow pytest.raises with wrong exception type
    "PT420",  # allow pytest.raises with wrong exception type
    "PT421",  # allow pytest.raises with wrong exception type
    "PT422",  # allow pytest.raises with wrong exception type
    "PT423",  # allow pytest.raises with wrong exception type
    "PT424",  # allow pytest.raises with wrong exception type
    "PT425",  # allow pytest.raises with wrong exception type
    "PT426",  # allow pytest.raises with wrong exception type
    "PT427",  # allow pytest.raises with wrong exception type
    "PT428",  # allow pytest.raises with wrong exception type
    "PT429",  # allow pytest.raises with wrong exception type
    "PT430",  # allow pytest.raises with wrong exception type
    "PT431",  # allow pytest.raises with wrong exception type
    "PT432",  # allow pytest.raises with wrong exception type
    "PT433",  # allow pytest.raises with wrong exception type
    "PT434",  # allow pytest.raises with wrong exception type
    "PT435",  # allow pytest.raises with wrong exception type
    "PT436",  # allow pytest.raises with wrong exception type
    "PT437",  # allow pytest.raises with wrong exception type
    "PT438",  # allow pytest.raises with wrong exception type
    "PT439",  # allow pytest.raises with wrong exception type
    "PT440",  # allow pytest.raises with wrong exception type
    "PT441",  # allow pytest.raises with wrong exception type
    "PT442",  # allow pytest.raises with wrong exception type
    "PT443",  # allow pytest.raises with wrong exception type
    "PT444",  # allow pytest.raises with wrong exception type
    "PT445",  # allow pytest.raises with wrong exception type
    "PT446",  # allow pytest.raises with wrong exception type
    "PT447",  # allow pytest.raises with wrong exception type
    "PT448",  # allow pytest.raises with wrong exception type
    "PT449",  # allow pytest.raises with wrong exception type
    "PT450",  # allow pytest.raises with wrong exception type
    "PT451",  # allow pytest.raises with wrong exception type
    "PT452",  # allow pytest.raises with wrong exception type
    "PT453",  # allow pytest.raises with wrong exception type
    "PT454",  # allow pytest.raises with wrong exception type
    "PT455",  # allow pytest.raises with wrong exception type
    "PT456",  # allow pytest.raises with wrong exception type
    "PT457",  # allow pytest.raises with wrong exception type
    "PT458",  # allow pytest.raises with wrong exception type
    "PT459",  # allow pytest.raises with wrong exception type
    "PT460",  # allow pytest.raises with wrong exception type
    "PT461",  # allow pytest.raises with wrong exception type
    "PT462",  # allow pytest.raises with wrong exception type
    "PT463",  # allow pytest.raises with wrong exception type
    "PT464",  # allow pytest.raises with wrong exception type
    "PT465",  # allow pytest.raises with wrong exception type
    "PT466",  # allow pytest.raises with wrong exception type
    "PT467",  # allow pytest.raises with wrong exception type
    "PT468",  # allow pytest.raises with wrong exception type
    "PT469",  # allow pytest.raises with wrong exception type
    "PT470",  # allow pytest.raises with wrong exception type
    "PT471",  # allow pytest.raises with wrong exception type
    "PT472",  # allow pytest.raises with wrong exception type
    "PT473",  # allow pytest.raises with wrong exception type
    "PT474",  # allow pytest.raises with wrong exception type
    "PT475",  # allow pytest.raises with wrong exception type
    "PT476",  # allow pytest.raises with wrong exception type
    "PT477",  # allow pytest.raises with wrong exception type
    "PT478",  # allow pytest.raises with wrong exception type
    "PT479",  # allow pytest.raises with wrong exception type
    "PT480",  # allow pytest.raises with wrong exception type
    "PT481",  # allow pytest.raises with wrong exception type
    "PT482",  # allow pytest.raises with wrong exception type
    "PT483",  # allow pytest.raises with wrong exception type
    "PT484",  # allow pytest.raises with wrong exception type
    "PT485",  # allow pytest.raises with wrong exception type
    "PT486",  # allow pytest.raises with wrong exception type
    "PT487",  # allow pytest.raises with wrong exception type
    "PT488",  # allow pytest.raises with wrong exception type
    "PT489",  # allow pytest.raises with wrong exception type
    "PT490",  # allow pytest.raises with wrong exception type
    "PT491",  # allow pytest.raises with wrong exception type
    "PT492",  # allow pytest.raises with wrong exception type
    "PT493",  # allow pytest.raises with wrong exception type
    "PT494",  # allow pytest.raises with wrong exception type
    "PT495",  # allow pytest.raises with wrong exception type
    "PT496",  # allow pytest.raises with wrong exception type
    "PT497",  # allow pytest.raises with wrong exception type
    "PT498",  # allow pytest.raises with wrong exception type
    "PT499",  # allow pytest.raises with wrong exception type
    "PT500",  # allow pytest.raises with wrong exception type
    "PT501",  # allow pytest.raises with wrong exception type
    "PT502",  # allow pytest.raises with wrong exception type
    "PT503",  # allow pytest.raises with wrong exception type
    "PT504",  # allow pytest.raises with wrong exception type
    "PT505",  # allow pytest.raises with wrong exception type
    "PT506",  # allow pytest.raises with wrong exception type
    "PT507",  # allow pytest.raises with wrong exception type
    "PT508",  # allow pytest.raises with wrong exception type
    "PT509",  # allow pytest.raises with wrong exception type
    "PT
## Python Code Style Guidelines

### 1. Naming Conventions

#### Variables and Functions
```python
# Use snake_case for variables and functions
user_name = "john_doe"
calculate_total_score()
get_package_info()

# Constants use UPPER_CASE
MAX_RETRIES = 3
API_BASE_URL = "https://libraries.io/api/v1"

# Private variables use leading underscore
_internal_cache = {}
_private_method()

# Protected variables use single leading underscore
_class_variable = "protected"
```

#### Classes and Methods
```python
# Use PascalCase for classes
class LibrariesIOClient:
    pass

class PackageInfo:
    pass

# Use snake_case for methods
class LibrariesIOClient:
    def get_package_info(self):
        pass
    
    def _internal_method(self):
        pass
    
    def __private_method(self):
        pass
```

#### Modules and Packages
```python
# Use lowercase with underscores
libraries_io_mcp/
client.py
server.py
models.py
```

### 2. Docstrings

#### Google Style Docstrings
```python
def get_package_info(platform: str, name: str) -> PackageInfo:
    """
    Retrieve package information from the Libraries.io API.
    
    Args:
        platform: Package manager platform (e.g., 'npm', 'pypi')
        name: Package name to retrieve information for
        
    Returns:
        PackageInfo: Object containing package information
        
    Raises:
        LibrariesIOClientError: If the API request fails
        ValueError: If platform or name is invalid
        
    Example:
        >>> client = LibrariesIOClient(api_key="your_key")
        >>> package = client.get_package_info("npm", "react")
        >>> print(package.name)
        'react'
    """
    pass
```

#### Class Docstrings
```python
class LibrariesIOClient:
    """
    A client for interacting with the Libraries.io API.
    
    This client provides methods to search for packages, get package information,
    and manage API rate limiting and caching.
    
    Attributes:
        api_key (str): API key for authentication
        base_url (str): Base URL for the API
        timeout (float): Request timeout in seconds
        max_retries (int): Maximum number of retry attempts
        
    Example:
        >>> client = LibrariesIOClient(api_key="your_key")
        >>> packages = await client.search_packages("react")
        >>> print(len(packages))
        10
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the LibrariesIOClient.
        
        Args:
            api_key: API key for authentication
            **kwargs: Additional configuration options
            
        Keyword Args:
            base_url: Base URL for the API (default: "https://libraries.io/api/v1")
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retry attempts (default: 3)
            cache_ttl: Cache TTL in seconds (default: 300)
        """
        pass
```

### 3. Type Hints

#### Basic Type Hints
```python
def get_package_name(package: PackageInfo) -> str:
    """Get package name."""
    return package.name

def process_packages(packages: List[PackageInfo]) -> Dict[str, PackageInfo]:
    """Process packages and return a dictionary."""
    return {pkg.name: pkg for pkg in packages}

def handle_request(request: Optional[Request]) -> Response:
    """Handle request with optional parameter."""
    if request is None:
        return Response()
    return process_request(request)
```

#### Union Types
```python
from typing import Union

def get_data(data: Union[str, bytes, bytearray]) -> str:
    """Get data as string."""
    if isinstance(data, (bytes, bytearray)):
        return data.decode('utf-8')
    return data

def process_result(result: Union[SuccessResponse, ErrorResponse]) -> bool:
    """Process result and return success status."""
    if isinstance(result, SuccessResponse):
        return True
    return False
```

#### Async Functions
```python
import asyncio
from typing import AsyncIterator

async def fetch_packages(query: str) -> AsyncIterator[PackageInfo]:
    """Fetch packages asynchronously."""
    async for package in package_stream:
        yield package

async def process_multiple_queries(queries: List[str]) -> List[PackageInfo]:
    """Process multiple queries concurrently."""
    tasks = [fetch_packages(query) for query in queries]
    results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]
```

### 4. Error Handling

#### Exception Hierarchy
```python
class LibrariesIOError(Exception):
    """Base exception for Libraries.io related errors."""
    pass

class LibrariesIOClientError(LibrariesIOError):
    """Exception raised when API client fails."""
    pass

class LibrariesIORateLimitError(LibrariesIOClientError):
    """Exception raised when rate limit is exceeded."""
    pass

class LibrariesIOAuthenticationError(LibrariesIOClientError):
    """Exception raised when authentication fails."""
    pass
```

#### Error Handling Patterns
```python
def get_package_info(platform: str, name: str) -> PackageInfo:
    """
    Get package info with proper error handling.
    
    Args:
        platform: Package manager platform
        name: Package name
        
    Returns:
        PackageInfo: Package information
        
    Raises:
        ValueError: If platform or name is invalid
        LibrariesIOClientError: If API request fails
    """
    # Validate input
    if not platform or not name:
        raise ValueError("Platform and name are required")
    
    try:
        # Make API request
        response = await self._make_request(f"/packages/{platform}/{name}")
        return PackageInfo(**response)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise LibrariesIOAuthenticationError("Invalid API key")
        elif e.response.status_code == 429:
            raise LibrariesIORateLimitError("Rate limit exceeded")
        else:
            raise LibrariesIOClientError(f"API request failed: {e}")
    except httpx.RequestError as e:
        raise LibrariesIOClientError(f"Network error: {e}")
    except Exception as e:
        raise LibrariesIOClientError(f"Unexpected error: {e}")
```

#### Context Managers
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def rate_limiter_context():
    """Context manager for rate limiting."""
    await self.rate_limiter.wait_if_needed()
    try:
        yield
    finally:
        self.rate_limiter.record_request()

async def get_package_with_rate_limit(platform: str, name: str) -> PackageInfo:
    """Get package info with rate limiting."""
    async with rate_limiter_context():
        return await self.get_package_info(platform, name)
```

### 5. Code Organization

#### Imports
```python
# Standard library imports first
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import logging

# Third-party imports second
import httpx
import pydantic
from fastmcp import Server

# Local imports third
from .models import PackageInfo, PlatformInfo
from .client import LibrariesIOClient
from .utils import validate_platform, sanitize_package_name
```

#### Module Structure
```python
# src/libraries_io_mcp/client.py
"""Libraries.io API client."""

from typing import Dict, List, Optional, AsyncIterator
import httpx
from .models import PackageInfo, PlatformInfo, SearchResults
from .utils import RateLimiter, Cache
from .exceptions import LibrariesIOError, LibrariesIOClientError

class LibrariesIOClient:
    """Client for interacting with the Libraries.io API."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize the client."""
        pass
    
    async def get_package_info(self, platform: str, name: str) -> PackageInfo:
        """Get package information."""
        pass
    
    async def search_packages(self, query: str, **kwargs) -> SearchResults:
        """Search for packages."""
        pass
    
    async def get_platforms(self) -> List[PlatformInfo]:
        """Get available platforms."""
        pass

__all__ = [
    "LibrariesIOClient",
    "LibrariesIOError",
    "LibrariesIOClientError",
]
```

### 6. Function Design

#### Function Length
```python
# Good: Short, focused functions
def validate_platform(platform: str) -> bool:
    """Validate platform name."""
    return platform in self.supported_platforms

def sanitize_package_name(name: str) -> str:
    """Sanitize package name."""
    return name.strip().lower().replace(" ", "-")

# Bad: Long, complex functions
def process_package_data(raw_data: Dict, platform: str, name: str) -> PackageInfo:
    """Process raw package data into PackageInfo object."""
    # Too many responsibilities
    pass
```

#### Function Parameters
```python
# Good: Reasonable number of parameters
def get_package_info(platform: str, name: str, include_versions: bool = False) -> PackageInfo:
    """Get package information."""
    pass

# Good: Use keyword arguments for optional parameters
def search_packages(
    query: str,
    platforms: Optional[List[str]] = None,
    languages: Optional[List[str]] = None,
    page: int = 1,
    per_page: int = 10
) -> SearchResults:
    """Search for packages."""
    pass

# Bad: Too many positional parameters
def get_package_info(platform, name, include_versions, include_dependencies, 
                    include_dependents, include_platforms, include_languages):
    """Too many parameters."""
    pass
```

#### Return Values
```python
# Good: Consistent return types
def get_package_info(platform: str, name: str) -> PackageInfo:
    """Return PackageInfo object."""
    return PackageInfo(...)

def search_packages(query: str) -> SearchResults:
    """Return SearchResults object."""
    return SearchResults(...)

# Good: Use Union for multiple return types
def process_data(data: Dict) -> Union[PackageInfo, ErrorResponse]:
    """Return either PackageInfo or ErrorResponse."""
    if data.get("error"):
        return ErrorResponse(**data)
    return PackageInfo(**data)
```

### 7. Class Design

#### Class Structure
```python
class LibrariesIOClient:
    """Client for interacting with the Libraries.io API."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize the client."""
        self.api_key = api_key
        self.base_url = kwargs.get("base_url", "https://libraries.io/api/v1")
        self.timeout = kwargs.get("timeout", 30.0)
        self.max_retries = kwargs.get("max_retries", 3)
        self.cache = Cache(kwargs.get("cache_ttl", 300))
        self.rate_limiter = RateLimiter(
            kwargs.get("rate_limit_requests", 100),
            kwargs.get("rate_limit_window", 3600)
        )
        self.http_client = httpx.AsyncClient(
            timeout=self.timeout,
            base_url=self.base_url
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.http_client.aclose()
    
    async def get_package_info(self, platform: str, name: str) -> PackageInfo:
        """Get package information."""
        pass
    
    async def search_packages(self, query: str, **kwargs) -> SearchResults:
        """Search for packages."""
        pass
    
    async def get_platforms(self) -> List[PlatformInfo]:
        """Get available platforms."""
        pass
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
```

#### Properties
```python
class PackageInfo:
    """Package information container."""
    
    def __init__(self, **kwargs):
        """Initialize package info."""
        self._data = kwargs
    
    @property
    def name(self) -> str:
        """Get package name."""
        return self._data.get("name", "")
    
    @property
    def platform(self) -> str:
        """Get package platform."""
        return self._data.get("platform", "")
    
    @property
    def stars(self) -> Optional[int]:
        """Get number of stars."""
        return self._data.get("stars")
    
    @property
    def is_popular(self) -> bool:
        """Check if package is popular."""
        return self.stars and self.stars > 1000
    
    @property
    def age(self) -> Optional[int]:
        """Get package age in days."""
        if not self.created_at:
            return None
        return (datetime.now() - self.created_at).days
```

### 8. Async/Await Patterns

#### Async Functions
```python
async def get_package_info(platform: str, name: str) -> PackageInfo:
    """Get package information asynchronously."""
    async with self.rate_limiter:
        response = await self.http_client.get(f"/packages/{platform}/{name}")
        response.raise_for_status()
        return PackageInfo(**response.json())

async def search_packages(query: str, **kwargs) -> SearchResults:
    """Search for packages asynchronously."""
    params = {"q": query, **kwargs}
    async with self.rate_limiter:
        response = await self.http_client.get("/search", params=params)
        response.raise_for_status()
        return SearchResults(**response.json())
```

#### Async Context Managers
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def rate_limited_request():
    """Context manager for rate limited requests."""
    await self.rate_limiter.wait_if_needed()
    try:
        yield
    finally:
        self.rate_limiter.record_request()

async def get_package_with_retry(platform: str, name: str) -> PackageInfo:
    """Get package info with retry logic."""
    for attempt in range(self.max_retries):
        try:
            async with rate_limited_request():
                return await self.get_package_info(platform, name)
        except LibrariesIOClientError as e:
            if attempt == self.max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

#### Async Iterators
```python
async def stream_packages(query: str) -> AsyncIterator[PackageInfo]:
    """Stream packages asynchronously."""
    page = 1
    while True:
        results = await self.search_packages(query, page=page, per_page=100)
        if not results.items:
            break
        
        for package in results.items:
            yield package
        
        page += 1

async def process_package_stream(query: str) -> List[PackageInfo]:
    """Process package stream."""
    packages = []
    async for package in stream_packages(query):
        packages.append(package)
        if len(packages) >= 1000:  # Limit processing
            break
    return packages
```

### 9. Data Structures

#### Lists and Dictionaries
```python
# Good: Use list comprehensions
package_names = [pkg.name for pkg in packages if pkg.stars > 1000]

# Good: Use dictionary comprehensions
package_dict = {pkg.name: pkg for pkg in packages}

# Good: Use sets for unique values
unique_platforms = {pkg.platform for pkg in packages}

# Good: Use defaultdict for counting
from collections import defaultdict
platform_counts = defaultdict(int)
for pkg in packages:
    platform_counts[pkg.platform] += 1
```

#### Custom Data Classes
```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class PackageStats:
    """Package statistics."""
    name: str
    platform: str
    stars: int
    forks: int
    issues: int
    contributors: int
    last_commit: Optional[datetime] = None
    
    @property
    def popularity_score(self) -> float:
        """Calculate popularity score."""
        return (self.stars * 0.4 + self.forks * 0.3 + self.contributors * 0.3)
    
    @property
    def is_active(self) -> bool:
        """Check if package is actively maintained."""
        if not self.last_commit:
            return False
        return (datetime.now() - self.last_commit).days < 30
```

### 10. Configuration Management

#### Configuration Classes
```python
from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_key: str = Field(..., env="LIBRARIES_IO_API_KEY")
    base_url: str = Field("https://libraries.io/api/v1", env="LIBRARIES_IO_BASE_URL")
    
    # Rate Limiting
    rate_limit_requests: int = Field(100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(3600, env="RATE_LIMIT_WINDOW")
    
    # Caching
    cache_ttl: int = Field(300, env="CACHE_TTL")
    
    # HTTP Client
    timeout: float = Field(30.0, env="TIMEOUT")
    max_retries: int = Field(3, env="MAX_RETRIES")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(None, env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

#### Configuration Usage
```python
import logging
from .settings import Settings

# Load settings
settings = Settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        *([logging.FileHandler(settings.log_file)] if settings.log_file else [])
    ]
)

logger = logging.getLogger(__name__)

# Use settings in client
client = LibrariesIOClient(
    api_key=settings.api_key,
    base_url=settings.base_url,
    timeout=settings.timeout,
    max_retries=settings.max_retries,
    cache_ttl=settings.cache_ttl
)
```

### 11. Logging

#### Logging Configuration
```python
import logging
import sys
from typing import Optional

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """Setup logging configuration."""
    
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=handlers
    )

# Usage
setup_logging(level="DEBUG", log_file="app.log")
logger = logging.getLogger(__name__)
```

#### Logging Patterns
```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class LibrariesIOClient:
    """Client for interacting with the Libraries.io API."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize the client."""
        self.api_key = api_key
        logger.info("Initializing LibrariesIOClient")
        
        # Log configuration
        logger.debug(f"Configuration - timeout: {kwargs.get('timeout', 30.0)}")
        logger.debug(f"Configuration - max_retries: {kwargs.get('max_retries', 3)}")
    
    async def get_package_info(self, platform: str, name: str) -> PackageInfo:
        """Get package information."""
        logger.info(f"Getting package info for {platform}/{name}")
        
        try:
            response = await self._make_request(f"/packages/{platform}/{name}")
            logger.debug(f"Successfully retrieved package info for {name}")
            return PackageInfo(**response)
        
        except LibrariesIOClientError as e:
            logger.error(f"Failed to get package info for {name}: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error getting package info for {name}")
            raise
    
    async def search_packages(self, query: str, **kwargs) -> SearchResults:
        """Search for packages."""
        logger.info(f"Searching for packages with query: {query}")
        logger.debug(f"Search parameters: {kwargs}")
        
        try:
            response = await self._make_request("/search", params={"q": query, **kwargs})
            logger.debug(f"Search returned {len(response.get('items', []))} results")
            return SearchResults(**response)
        
        except LibrariesIOClientError as e:
            logger.error(f"Search failed for query '{query}': {e}")
            raise
```

### 12. Testing Patterns

#### Test Structure
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.libraries_io_mcp.client import LibrariesIOClient
from src.libraries_io_mcp.models import PackageInfo

class TestLibrariesIOClient:
    """Test suite for LibrariesIOClient."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return LibrariesIOClient(api_key="test_key")
    
    @pytest.fixture
    def mock_response(self):
        """Create mock response."""
        mock = AsyncMock()
        mock.status_code = 200
        mock.json.return_value = {
            "name": "react",
            "platform": "npm",
            "description": "A JavaScript library"
        }
        return mock
    
    @pytest.mark.asyncio
    async def test_get_package_info_success(self, client, mock_response):
        """Test successful package info retrieval."""
        # Setup
        client.http_client.get = AsyncMock(return_value=mock_response)
        
        # Execute
        result = await client.get_package_info("npm", "react")
        
        # Assert
        assert result.name == "react"
        assert result.platform == "npm"
        assert result.description == "A JavaScript library"
        
        # Verify HTTP call
        client.http_client.get.assert_called_once_with(
            "/packages/npm/react",
            params={"include_versions": False}
        )
    
    @pytest.mark.asyncio
    async def test_get_package_info_error(self, client):
        """Test package info retrieval with error."""
        # Setup
        mock_response = AsyncMock()
        mock_response.status_code = 404
        client.http_client.get = AsyncMock(return_value=mock_response)
        
        # Execute
        with pytest.raises(LibrariesIOClientError):
            await client.get_package_info("npm", "nonexistent")
```

#### Mock Patterns
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

class TestLibrariesIOClient:
    """Test suite for LibrariesIOClient."""
    
    @pytest.mark.asyncio
    async def test_with_mock_client(self):
        """Test with mocked HTTP client."""
        # Create mock client
        mock_http_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "react"}
        mock_http_client.get.return_value = mock_response
        
        # Create client with mock
        client = LibrariesIOClient(api_key="test_key")
        client.http_client = mock_http_client
        
        # Execute
        result = await client.get_package_info("npm", "react")
        
        # Assert
        assert result.name == "react"
    
    @pytest.mark.asyncio
    async def test_with_patch(self):
        """Test with patch decorator."""
        with patch('src.libraries_io_mcp.client.httpx.AsyncClient') as mock_client_class:
            # Setup mock
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"name": "react"}
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client
            
            # Create client
            client = LibrariesIOClient(api_key="test_key")
            
            # Execute
            result = await client.get_package_info("npm", "react")
            
            # Assert
            assert result.name == "react"
```

### 13. Performance Patterns

#### Caching Patterns
```python
import functools
from typing import Optional
from datetime import datetime, timedelta

def cache_with_ttl(ttl: int):
    """Decorator for caching with TTL."""
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            if cache_key in cache:
                cached_result, cached_time = cache[cache_key]
                if datetime.now() - cached_time < timedelta(seconds=ttl):
                    return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache[cache_key] = (result, datetime.now())
            
            return result
        
        return wrapper
    return decorator

class LibrariesIOClient:
    """Client with caching."""
    
    @cache_with_ttl(ttl=300)  # 5 minutes cache
    async def get_package_info(self, platform: str, name: str) -> PackageInfo:
        """Get package information with caching."""
        response = await self._make_request(f"/packages/{platform}/{name}")
        return PackageInfo(**response)
```

#### Performance Monitoring
```python
import time
import functools
from typing import Callable, Any

def monitor_performance(func: Callable) -> Callable:
    """Decorator for monitoring performance."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Log performance
            logger.info(
                f"Function {func.__name__} executed in {execution_time:.2f}s"
            )
            
            # Log slow functions
            if execution_time > 1.0:
                logger.warning(
                    f"Function {func.__name__} took {execution_time:.2f}s (slow)"
                )
    
    return wrapper

class LibrariesIOClient:
    """Client with performance monitoring."""
    
    @monitor_performance
    async def search_packages(self, query: str, **kwargs) -> SearchResults:
        """Search for packages with performance monitoring."""
        response = await self._make_request("/search", params={"q": query, **kwargs})
        return SearchResults(**response)
```

### 14. Security Patterns

#### Input Validation
```python
import re
from typing import Optional
from pydantic import BaseModel, validator

class PackageRequest(BaseModel):
    """Package request model with validation."""
    
    platform: str
    name: str
    
    @validator('platform')
    def validate_platform(cls, v):
        """Validate platform name."""
        if not v or not isinstance(v, str):
            raise ValueError("Platform must be a non-empty string")
        
        # Check for valid platform names
        valid_platforms = {'npm', 'pypi', 'maven', 'rubygems', 'nuget', 'cargo'}
        if v.lower() not in valid_platforms:
            raise ValueError(f"Invalid platform: {v}")
        
        return v.lower()
    
    @validator('name')
    def validate_name(cls, v):
        """Validate package name."""
        if not v or not isinstance(v, str):
            raise ValueError("Name must be a non-empty string")
        
        # Remove whitespace and special characters
        v = v.strip()
        
        # Basic validation for package names
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError("Package name contains invalid characters")
        
        return v

class LibrariesIOClient:
    """Client with input validation."""
    
    async def get_package_info(self, platform: str, name: str) -> PackageInfo:
        """Get package info with validation."""
        # Validate input
        request = PackageRequest(platform=platform, name=name)
        
        # Make API request
        response = await self._make_request(
            f"/packages/{request.platform}/{request.name}"
        )
        return PackageInfo(**response)
```

#### Security Headers
```python
import httpx
from typing import Dict, Optional

class SecureHTTPClient:
    """HTTP client with security headers."""
    
    def __init__(self, **kwargs):
        """Initialize secure HTTP client."""
        self.timeout = kwargs.get("timeout", 30.0)
        self.base_url = kwargs.get("base_url", "https://libraries.io/api/v1")
        
        # Configure security headers
        self.default_headers = {
            "User-Agent": "LibrariesIO-MCP-Server/1.0",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
        }
        
        self.http_client = httpx.AsyncClient(
            timeout=self.timeout,
            base_url=self.base_url,
            headers=self.default_headers
        )
    
    async def make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make secure HTTP request."""
        # Add security headers
        headers = kwargs.get("headers", {})
        headers.update(self.default_headers)
        kwargs["headers"] = headers
        
        # Validate URL
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        # Make request
        response = await self.http_client.request(method, url, **kwargs)
        
        # Check for security issues
        self._check_security_headers(response)
        
        return response
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL."""
        if not url or not isinstance(url, str):
            return False
        
        # Check for protocol
        if not url.startswith(("http://", "https://")):
            return False
        
        # Check for malicious characters
        malicious_chars = ["<", ">", "'", '"', ";", "|", "&", "$"]
        if any(char in url for char in malicious_chars):
            return False
        
        return True
    
    def _check_security_headers(self, response: httpx.Response) -> None:
        """Check response security headers."""
        # Check for sensitive information in headers
        sensitive_headers = ["set-cookie", "authorization", "api-key"]
        for header in sensitive_headers:
            if header.lower() in response.headers:
                logger.warning(f"Sensitive header found: {header}")
        
        # Check for security-related headers
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
            "strict-transport-security"
        ]
        
        missing_headers = []
        for header in security_headers:
            if header.lower() not in response.headers:
                missing_headers.append(header)
        
        if missing_headers:
            logger.warning(f"Missing security headers: {missing_headers}")
```

### 15. Code Review Checklist

#### Code Review Items
```markdown
## Code Review Checklist

### Code Quality
- [ ] Code follows project style guidelines
- [ ] Code is properly documented with docstrings
- [ ] Type hints are used consistently
- [ ] Error handling is comprehensive
- [ ] Code is testable and tested

### Performance
- [ ] Code is efficient and doesn't have obvious performance issues
- [ ] Caching is used appropriately
- [ ] Database queries are optimized
- [ ] Memory usage is reasonable

### Security
- [ ] Input validation is implemented
- [ ] Output encoding is used
- [ ] Security headers are set
- [ ] No hardcoded secrets or sensitive data
- [ ] SQL injection prevention is in place

### Architecture
- [ ] Code follows project architecture patterns
- [ ] Dependencies are properly managed
- [ ] Code is modular and maintainable
- [ ] Design patterns are used appropriately

### Testing
- [ ] Unit tests are comprehensive
- [ ] Integration tests are in place
- [ ] Edge cases are covered
- [ ] Test coverage is adequate

### Documentation
- [ ] Code is well-documented
- [ ] README is updated if needed
- [ ] API documentation is current
- [ ] Examples are provided

### Compatibility
- [ ] Code works across supported Python versions
- [ ] Dependencies are compatible
- [ ] Platform-specific code is handled
- [ ] Backward compatibility is maintained

### Deployment
- [ ] Code is deployment-ready
- [ ] Configuration is externalized
- [ ] Logging is appropriate
- [ ] Monitoring is in place
```

### 16. Development Workflow

#### Pre-commit Hooks
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running pre-commit checks..."

# Format code
echo "Formatting code with black..."
black src/ tests/
echo "Sorting imports with isort..."
isort src/ tests/

# Lint code
echo "Linting code with flake8..."
flake8 src/ tests/

# Type check
echo "Type checking with mypy..."
mypy src/

# Run tests
echo "Running tests..."
pytest tests/

echo "Pre-commit checks completed successfully!"
```

#### Development Setup
```bash
#!/bin/bash
# scripts/setup-dev.sh

echo "Setting up development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

echo "Development environment setup complete!"
```

#### Code Quality Script
```bash
#!/bin/bash
# scripts/quality-check.sh

echo "Running code quality checks..."

# Format code
echo "Formatting code..."
black src/ tests/
isort src/ tests/

# Lint code
echo "Linting code..."
flake8 src/ tests/

# Type check
echo "Type checking..."
mypy src/

# Security check
echo "Running security checks..."
bandit -r src/

# Run tests
echo "Running tests..."
pytest tests/ --cov=src --cov-report=html --cov-report=term

echo "Code quality checks completed!"
```

## Conclusion

This comprehensive code style guide provides detailed guidelines for maintaining high-quality, consistent, and maintainable code in the Libraries.io MCP Server project. By following these guidelines and using the provided tools and patterns, developers can ensure that the codebase remains clean, readable, and efficient.

### Key Takeaways

1. **Use Automated Tools**: Black, isort, flake8, mypy, and ruff should be used to enforce code style automatically
2. **Follow Python Standards**: Adhere to PEP 8 and Python best practices
3. **Write Comprehensive Docstrings**: Use Google-style docstrings for all public functions and classes
4. **Type Everything**: Use type hints consistently throughout the codebase
5. **Handle Errors Properly**: Use appropriate exception types and provide meaningful error messages
6. **Keep Functions Small**: Focus on single responsibilities and keep functions short and focused
7. **Write Tests**: Ensure comprehensive test coverage for all code
8. **Monitor Performance**: Use caching and performance monitoring where appropriate
9. **Prioritize Security**: Validate input, use security headers, and prevent common vulnerabilities
10. **Document Everything**: Provide clear documentation for APIs, configuration, and deployment

### Resources

- [PEP 8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Black Code Formatter](https://black.readthedocs.io/)
- [isort Import Sorting](https://pycqa.github.io/isort/)
- [flake8 Linter](https://flake8.pycqa.org/)
- [mypy Type Checker](https://mypy.readthedocs.io/)
- [ruff Linter](https://github.com/astral-sh/ruff)

By following these guidelines and using the provided tools, the Libraries.io MCP Server project will maintain high code quality standards throughout its development lifecycle.