# inverted_and_positional_index
HW1 under Text Retrieval and Search Engines course at Reichman University

# inverted_and_positional_index

**HW1 under Text Retrieval and Search Engines course at Reichman University**

A Python implementation of an inverted index and Boolean retrieval model for document search.

---

## Features

- **Inverted Index** - Builds an index from AP document collection
- **Boolean Queries** - Supports AND, OR, and NOT operations using Reverse Polish Notation (RPN)
- **Collection Statistics** - Analyzes term frequencies and finds similar terms
- **Efficient Retrieval** - O(N+M) complexity for Boolean operations

---

## Requirements

Python 3.x

---

## File Structure
```
project/
├── data/
│   ├── docs/              # AP document collection
│   └── BooleanQueries.txt
└── script.py              # Main code
```

---

## Usage

### Build inverted index
```python
index = InvertedIndex()
index.build_index()
```

### Retrieve data structures
```python
inverted_index = index.get_index()
doc_mapper = index.get_doc_id_map()
```

### Execute Boolean queries
```python
bool_retrieval = BooleanRetrieval()
bool_retrieval.retrieve(inverted_index, doc_mapper)
```

### Get collection statistics
```python
index.sort_docs_frequency()
print(index.get_top_10_terms())
print(index.get_lowest_10_terms())
print(index.find_similar_terms())
```

---

## Query Format

Boolean queries use Reverse Polish Notation (RPN):
```
term1 term2 AND
term1 term2 OR
term1 term2 NOT    # Returns: term1 AND NOT term2
```

---

## Output

`Part_2.txt` - Document IDs matching each Boolean query (one query per line)