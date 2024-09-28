<?php
session_start();


if (!isset($_SESSION['name'])) {
    session_unset(); // Clear session variables
}

// Battleship Game Class
class BattleshipGame {
    private $rows = 5;
    private $cols = 7;
    private $board;
    private $ships = [];
    private $moves_left;
    private $hits = 0;
    private $max_hits;
    public $game_over = false;

    // Constructor to initialize game
    public function __construct() {
        $this->initialize_board();
        $this->max_hits = 2 + 3 + 4; 
        $this->moves_left = ceil($this->rows * $this->cols * 0.60);
        $this->place_ship(2); // 2x1 ship
        $this->place_ship(3); // 3x1 ship
        $this->place_ship(4); // 4x1 ship
    }

    // Function to initialize the board
    private function initialize_board() {
        $this->board = array_fill(0, $this->rows, array_fill(0, $this->cols, '?'));
    }

    // Function to place a ship on the board
    private function place_ship($size) {
        $valid_placement = false;

        while (!$valid_placement) {
            $direction = rand(0, 1) === 0 ? 'horizontal' : 'vertical';
            $row = rand(0, $this->rows - 1);
            $col = rand(0, $this->cols - 1);

            if ($direction === 'horizontal' && $col + $size <= $this->cols) {
                $valid_placement = $this->check_valid_ship_placement($row, $col, $size, 'horizontal');
                if ($valid_placement) {
                    for ($i = 0; $i < $size; $i++) {
                        $this->ships["$row," . ($col + $i)] = true;
                    }
                }
            } elseif ($direction === 'vertical' && $row + $size <= $this->rows) {
                $valid_placement = $this->check_valid_ship_placement($row, $col, $size, 'vertical');
                if ($valid_placement) {
                    for ($i = 0; $i < $size; $i++) {
                        $this->ships[($row + $i) . ",$col"] = true;
                    }
                }
            }
        }
    }

    // Helper function to check if the ship placement is valid
    private function check_valid_ship_placement($row, $col, $size, $direction) {
        for ($i = 0; $i < $size; $i++) {
            if ($direction === 'horizontal' && isset($this->ships["$row," . ($col + $i)])) {
                return false;
            }
            if ($direction === 'vertical' && isset($this->ships[($row + $i) . ",$col"])) {
                return false;
            }
        }
        return true;
    }

    // Function to handle a player's move
    public function make_move($row, $col) {
        if ($this->board[$row][$col] === '?') {
            if (isset($this->ships["$row,$col"])) {
                $this->board[$row][$col] = 'X';
                $this->hits++;
            } else {
                $this->board[$row][$col] = 'O';
            }
            $this->moves_left--;

            // Check game over conditions
            if ($this->hits == $this->max_hits) {
                $this->game_over = "You win!";
            } elseif ($this->moves_left == 0) {
                $this->game_over = "You lose!";
            }
        }
    }

    // Function to get the current board state
    public function get_board() {
        return $this->board;
    }

    // Function to get the remaining moves
    public function get_moves_left() {
        return $this->moves_left;
    }

    // Function to reset the game
    public function reset_game() {
        $this->initialize_board();
        $this->ships = [];
        $this->hits = 0;
        $this->game_over = false;
        $this->max_hits = 2 + 3 + 4;
        $this->moves_left = ceil($this->rows * $this->cols * 0.60);
        $this->place_ship(2);
        $this->place_ship(3);
        $this->place_ship(4);
    }
}

// Handle the game logic
if (!isset($_SESSION['game'])) {
    $_SESSION['game'] = new BattleshipGame();
}

$game = $_SESSION['game'];

// Handle name submission
if (isset($_POST['name'])) {
    $_SESSION['name'] = $_POST['name'];
}

// Handle move submission
if (isset($_POST['move']) && !$game->game_over) {
    list($row, $col) = explode(",", $_POST['move']);
    $game->make_move($row, $col);
}

// Handle "Play again"
if (isset($_POST['play_again'])) {
    $game->reset_game();
}

// HTML output starts here
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="battleship.css">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Battleship Game</title>
    <style>
        table { border-collapse: collapse; }
        td { width: 30px; height: 30px; text-align: center; border: 1px solid black; }
    </style>
</head>
<body>
    <?php if (!isset($_SESSION['name'])): ?>
        <form method="POST">
            <label for="name">Enter your name: </label>
            <input type="text" id="name" name="name" required>
            <button type="submit">Submit</button>
        </form>
    <?php else: ?>
        <p>Hello, <?= htmlspecialchars($_SESSION['name']); ?>! Current time: <?= date('H:i:s'); ?></p>
        <p>Moves left: <?= $game->get_moves_left(); ?></p>

        <form method="POST">
            <table>
                <?php $board = $game->get_board(); ?>
                <?php for ($row = 0; $row < 5; $row++): ?>
                    <tr>
                        <?php for ($col = 0; $col < 7; $col++): ?>
                            <td class="
                                <?php if ($board[$row][$col] === 'X') {
                                    echo 'hit';
                                } elseif ($board[$row][$col] === 'O') {
                                    echo 'miss';
                                } else {
                                    echo 'default';
                                } ?>">
                                <?php if ($game->game_over): ?>
                                    <?= $board[$row][$col]; ?>
                                <?php else: ?>
                                    <button type="submit" name="move" value="<?= "$row,$col"; ?>">
                                        <?= $board[$row][$col]; ?>
                                    </button>
                                <?php endif; ?>
                            </td>
                        <?php endfor; ?>
                    </tr>
                <?php endfor; ?>
            </table>
        </form>

        <?php if ($game->game_over): ?>
            <p><?= $game->game_over; ?></p>
            <form method="POST">
                <button id="again" type="submit" name="play_again">Play again</button>
            </form>
        <?php endif; ?>
    <?php endif; ?>
</body>
</html>
