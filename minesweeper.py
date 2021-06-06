import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def __repr__(self):
        return str(self)

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_move(self, cell):
        """
        Marks the cell as having being clicked on
        """

        self.moves_made.add(cell)

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        # import pdb

        # pdb.set_trace()
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def get_neighbours(self, cell):
        """
        Get all neighbours of a cell
        """

        # import pdb

        # pdb.set_trace()
        neighbours = set()
        possible_cols = set()
        possible_rows = set()

        col = cell[0]

        possible_cols.add(col)
        if col - 1 >= 0:
            possible_cols.add(col - 1)
        if col + 1 <= self.height - 1:
            possible_cols.add(col + 1)

        row = cell[1]

        possible_rows.add(row)
        if row - 1 >= 0:
            possible_rows.add(row - 1)
        if row + 1 <= self.width - 1:
            possible_rows.add(row + 1)

        for col in possible_cols:
            for row in possible_rows:
                neighbour_cell = (col, row)
                if (
                    cell != neighbour_cell
                    and neighbour_cell not in self.moves_made
                    and neighbour_cell not in self.safes
                    and neighbour_cell not in self.mines
                ):
                    neighbours.add(neighbour_cell)

        return neighbours

    def generate_inferences(self):
        """
        Try to generate new sentences from existing knowledge

        e.g. if knowlege = [{(7, 7), (6, 5), (6, 6), (7, 5)} = 3, {(6, 6), (5, 6), (5, 7), (7, 7)} = 2]
        then new sentence is that {(7, 5), (6, 5)} = 1

        Compare each sentence to all others
        If there are any common cells and the count is larger, perform a substraction
        on both the set of cells and the count to generate a new sentence

        Then add that sentence to the knowldge
        """

        # import pdb

        # pdb.set_trace()
        # for sentence_one in self.knowledge:
        #     for sentence_two in self.knowledge:
        #         if (
        #             sentence_one.cells == sentence_two.cells
        #             and sentence_one.count == sentence_two.count
        #         ):
        #             continue

        for sentence_one, sentence_two in itertools.combinations(self.knowledge, 2):

            intersection = sentence_one.cells.intersection(sentence_two.cells)

            if intersection and sentence_one.count >= sentence_two.count:
                cells = intersection
                count = sentence_one.count - sentence_two.count

                sentence = Sentence(cells=cells, count=count)

                for existing_sentence in self.knowledge:
                    if (
                        cells == existing_sentence.cells
                        and count > existing_sentence.count
                    ):
                        self.knowledge.remove(existing_sentence)

                if sentence not in self.knowledge:
                    print(f"New sentence: {sentence}")
                    self.knowledge.append(sentence)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # import pdb

        # pdb.set_trace()
        self.mark_move(cell)
        self.mark_safe(cell)

        neighbours = self.get_neighbours(cell)
        sentence = Sentence(cells=neighbours, count=count)
        self.knowledge.append(sentence)

        if count == 0:
            for neighbouring_cell in neighbours:
                self.mark_safe(neighbouring_cell)

        if len(neighbours) == count and count > 0:
            print(f"Marking mines: {neighbours}, {count}")

            for neighbouring_cell in neighbours:
                self.mark_mine(neighbouring_cell)

        self.generate_inferences()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        moves = self.safes - self.moves_made - self.mines

        if not moves:

            return None

        return moves.pop()

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        print(self.knowledge)

        moves = self.moves_made - self.mines

        x = random.randint(0, self.height - 1)
        y = random.randint(0, self.width - 1)

        if (x, y) not in moves and (x, y) not in self.mines:
            print(f"--> AI making random move: {(x, y)}")
            return (x, y)

        return None
