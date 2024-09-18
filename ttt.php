<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tic-Tac-Toe</title>
    <link rel="stylesheet" href="ttt.css"> <!-- Link to the CSS file -->
</head>
<body>
    <?php
    $moves = [0, 1, 2, 3, 4, 5, 6, 7, 8];
    function display_board($board, $name) {
        $moves = get_possible_moves($board);
        echo '<table>';
        for ($i = 0; $i < 3; $i++) {
            echo '<tr>';
            for ($j = 0; $j < 3; $j++) {
                $index = $i * 3 + $j;
                $url_index = goto_index($board, $index);
                if ($url_index == strlen($board)) {
                    $cell = ' ';
                }
                else{
                    $cell = $board[$url_index];
                }
                if ($cell === ' ') {
                    // Create a new board string with the move placed
                    
                    $updated_moves = $moves;
                    $key = array_search($index, $updated_moves);

                    if ($key !== false) {
                        // Remove the value from the array
                        unset($updated_moves[$key]);
                        $updated_moves = array_values($updated_moves);//reindex it
                    }
                    // print(" ". implode(', ', $updated_moves) . " Move: " . $index . " ");
                    if (count($updated_moves) > 0) {//you can choose opponenet move
                        $opponent_url = opponent_move($board, $updated_moves);
                        if ($url_index > $opponent_url){//O then X
                            $new_board_str = urlencode(substr($board, 0, $opponent_url) . "O" .
                                substr($board, $opponent_url, $url_index - $opponent_url) . "X" .
                                substr($board, $url_index)
                            ); // Encode spaces for the URL
                        }
                        else {//X then O
                            $new_board_str = urlencode(substr($board, 0, $url_index) . "X" .
                                substr($board, $url_index, $opponent_url - $url_index) . "O" .
                                substr($board, $opponent_url)
                            ); // Encode spaces for the URL
                        }
                    }
                    else{//final move
                        $new_board_str = urlencode(substr($board, 0, $url_index) . "X" . substr($board, $url_index)); // Encode spaces for the URL
                    }
                    // Create the link to the same page with the updated board
                    // echo '<br>';
                    
                    
                    echo "<td><a href='ttt.php?name=$name&board=$new_board_str'>_</a></td>";
                } else {
                    // Display X or O
                    echo "<td>$cell</td>";
                }
            }
            echo '</tr>';
        }
        echo '</table>';
    }

    function goto_index($board, $index){
        $space = 0;
        $pointer = 0;
        $length = strlen($board);  // Length of the board string

        while ($space < $index && $pointer < $length) {
            if ($board[$pointer] == ' ') {
                $space++;
            }
            $pointer++;
        }
        return $pointer;
    }

    function get_possible_moves($board){
        $moves = [];
        $pointer = 0;
        $length = strlen($board);  // Length of the board string

        for ($i = 0; $i < 8; $i++){
            if ($board[$pointer] == ' '){//there is a move here
                $moves[] = $i;
                $pointer++;
                continue;
            }
            else if ($pointer < $length && $board[$pointer] != ' ') {
                $pointer+=2;
            }
        }
        if ($pointer == $length && $board[$pointer-1] == " "){
            $moves[] = 8;
        }
        return $moves;
    }
    function check_winner($board) {
        // print("a".$board."b");
        // Winning combinations
        $winning_combinations = [
            [0, 1, 2], // Row 1
            [3, 4, 5], // Row 2
            [6, 7, 8], // Row 3
            [0, 3, 6], // Column 1
            [1, 4, 7], // Column 2
            [2, 5, 8], // Column 3
            [0, 4, 8], // Diagonal 1
            [2, 4, 6], // Diagonal 2
        ];
        if (strlen($board) == 8) {
            $board = $board . " ";
        }
        foreach ($winning_combinations as $combo) {
            // Check if the three values in the combo are the same and not empty
            $a = goto_index($board, $combo[0]);
            $b = goto_index($board, $combo[1]);
            $c = goto_index($board, $combo[2]);
            $len = strlen($board);
            ($a == $len) ? $a = " " : $a = $board[$a];//if they are looking at the end, past the str, it means there is a move in the last cell
            ($b == $len) ? $b = " " : $b = $board[$b];
            ($c == $len) ? $c = " " : $c = $board[$c];
            if ($a != ' ' && $a == $b && $b == $c) {
                return $a; // Return 'X' or 'O'
            }
        }
    
        // Check for a draw (no empty spaces)
        if (substr_count($board, "X") + substr_count($board, "O") == 9) {
            return 'Draw';
        }
    
        // Game is still ongoing
        return null;
    }

    function opponent_move($board, $moves) {
        $key = array_rand($moves);//get the key
        $index = $moves[$key];
        unset($moves[$key]);//remove the random element
        $moves = array_values($moves);//reindex it
        $url_index = goto_index( $board, $index );
    
        //echo " Opponent Move: $index";
        return $url_index;//this is the move that the opponent is going to make
    }

    // Check if 'name' is present in the GET request
    if (isset($_GET['name']) && !empty($_GET['name'])) {
        // Get the 'name' from the query string
        $name = htmlspecialchars($_GET['name']); // Sanitize for security
        // Get the current date
        date_default_timezone_set('America/New_York');
        $date = date('m/d/y, h:i A'); // Example: "Saturday, September 14, 2024"

        if (isset($_GET['board'])) {
            $board = urldecode($_GET['board']);
        } else {
            $board = '        '; // 9 spaces for an empty board
        }
        $win = check_winner($board);
        echo "
        <div class='form_box'>
        <h1>Hello, $name!</h1>
        <p>Today's date is $date.</p>
        ";
        if ($win == null){//game isn't over yet
            display_board($board, $name);
        }
        echo '</div>';
        if ($win == "X") {
            echo "You won!";
            echo "<a href='ttt.php?name=$name'>Play again</a>";
        }
        else if ($win == "O") {
            echo "I won!";
            echo "<a href='ttt.php?name=$name'>Play again</a>";
        }
        else if ($win == "Draw") {
            echo '
                WINNER: NONE. A STRANGE GAME. THE ONLY WINNING MOVE IS NOT TO PLAY.
            ';
        }
    } else {
        // If 'name' is not provided, display the form
        echo '
        <div class="form_box">
        <h1>Welcome to Tic Tac Toe!</h1>
        <form method="GET" action="ttt.php" class="box">
            <label for="name" >Enter your name:</label>
            <input type="text" id="name" name="name" required>
            <input type="submit" value="Submit">
        </form>
        </div>
        ';
    }
    ?>
</body>
</html>