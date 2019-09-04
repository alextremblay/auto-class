Changelog
=========

Version 1.0
-----------

- Completely re-written from the ground up
- Makes use of an intermediate representation, meaning a list of API responses / json 
  objects can analyzed and parsed into IR, converted to YAML for additional annotation 
  by the user, converted back into IR, processed into dataclass definitions, converted 
  back into yaml if additional user input is needed, and so on.
- Can handle almost every input data edge-case I can think of (dataclasses in dataclasses, 
  dataclasses in lists, dataclasses in `Union`s, lists in lists, lists in unions, etc)

Version 0.1
-----------

- Initial working implementation. recursively parses an input yaml 
  manifest and pushes dataclass definitions to a global stack
- Doesn't handle edge-cases (at all)
- Is a single-pass, one-way operation, with no refinement or double-checking. 
  No ability to convert back to YAML and prompt user for additional info if needed.
- Not adaptable to parsing lists of api response objects and analyzing them
- Needs heavy refactoring
