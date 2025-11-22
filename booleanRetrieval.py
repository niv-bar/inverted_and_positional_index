from invertedIndex import InvertedIndex


class BooleanRetrieval:
    """
    Boolean retrieval model supporting AND, OR, and AND-NOT operations
    Complexity: O(N+M)
    """
    def __init__(self):
        self.operators = {"AND", "OR", "NOT"}  # Allowed Boolean operators

    def retrieve(
        self,
        inverted_index: dict[str, list[int]],
        doc_map: dict[int, str],
        query_file_path: str = "BooleanQueries.txt",
        output_file_path: str = "Part_2.txt"
        ) -> None:
        """Evaluate Boolean RPN queries and write matching document IDs to file."""
        # Open file (Part_2) for writing
        with open(output_file_path, "w", encoding="utf-8") as out_f:

            # Open queries file
            with open(query_file_path, "r", encoding="utf-8") as in_f:
                # Break into lines
                lines = [line.strip() for line in in_f]

            # Iterate each line
            for line in lines:
                # Skip empty lines
                if not line:
                    continue

                print(f"Processing retrieval for query: {line}")

                tokens = line.split()  # Tokenize the current query

                # Retrieve the final result list
                final_internal_ids = self._execute_query_retrieval(tokens, inverted_index)

                # Convert internal_ids into original_ids
                original_ids = [doc_map[internal_id] for internal_id in final_internal_ids]

                # Write a line in the open file (a single query)
                output_line = " ".join(original_ids)
                out_f.write(output_line + "\n")
            
            print(f"Boolean retrieval results written to {output_file_path}")

    def _execute_query_retrieval(
            self,
            tokens: list[str],
            inverted_index: dict[str, list[int]]
            ) -> list[int]:
        """Retrieve relevant docs list for the quesry."""
        stack = []

        # Iterate each token in the query
        for token in tokens:
            # if token is a term, assuming there are no terms that are the same as operators
            if token not in self.operators:
                # get the posting list of the relevant term and append it to the stack
                postings_ids = inverted_index.get(token, [])
                stack.append(postings_ids)

            # if token is an operator
            else:
                # Retrieve the posting lists in reverse order
                r2 = stack.pop()  # Right operand
                r1 = stack.pop()  # Left Operand

                result = []
                # Apply the required operator logic
                if token == "AND":
                    result = self.__intersect(r1, r2)
                elif token == "OR":
                    result = self.__union(r1, r2)
                # r1 AND NOT r2
                elif token == "NOT":
                    result = self.__difference(r1, r2)

                # Push the result list into the stack
                stack.append(result)

        return stack.pop()

    # AND
    @staticmethod
    def __intersect(l1_ids: list[int], l2_ids: list[int]) -> list[int]:
        """Return intersection (AND) of two sorted posting lists."""
        intersection = []
        i = j = 0

        while i < len(l1_ids) and j < len(l2_ids):
            if l1_ids[i] == l2_ids[j]:
                intersection.append(l1_ids[i])
                i += 1
                j += 1

            elif l1_ids[i] < l2_ids[j]:
                i += 1

            else:
                j += 1

        return intersection

    # OR
    @staticmethod
    def __union(l1_ids: list[int], l2_ids: list[int]) -> list[int]:
        """Return union (OR) of two sorted posting lists."""
        union_result = []
        i = j = 0

        while i < len(l1_ids) and j < len(l2_ids):

            if l1_ids[i] <= l2_ids[j]:
                union_result.append(l1_ids[i])
                i += 1
                j += 1

            elif l1_ids[i] < l2_ids[j]:
                union_result.append(l1_ids[i])
                i += 1

            else:
                union_result.append(l2_ids[j])
                j += 1

        # Append remaining elements
        while i < len(l1_ids):
            union_result.append(l1_ids[i])
            i += 1

        while j < len(l2_ids):
            union_result.append(l2_ids[j])
            j += 1

        return union_result

    # AND NOT
    @staticmethod
    def __difference(l1_ids: list[int], l2_ids: list[int]) -> list[int]:
        """Return difference (r1 AND NOT r2) between two sorted posting lists."""
        difference_result = []
        i = j = 0

        while i < len(l1_ids) and j < len(l2_ids):
            if l1_ids[i] == l2_ids[j]:
                i += 1
                j += 1

            elif l1_ids[i] < l2_ids[j]:
                difference_result.append(l1_ids[i])
                i += 1

            else:
                j += 1

        # Append remaining elements in l1
        while i < len(l1_ids):
            difference_result.append(l1_ids[i])
            i += 1

        return difference_result
    

if __name__ == "__main__":
    # Build inverted index
    index = InvertedIndex()
    index.build_index()

    # Retrieve data structures
    revert_index = index.get_index()
    doc_mapper = index.get_doc_id_map()

    # Print first 10 terms for inspection
    first_keys = list(revert_index.keys())[:10]
    for key in first_keys:
        values = revert_index[key]
        print(key, values[:10])

    # Boolean retrieval
    bool_retrieval = BooleanRetrieval()
    bool_retrieval.retrieve(revert_index, doc_mapper)
