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
    function display_board($board, $name) {
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
                    
                    
                    // Create the link to the same page with the updated board
                    $new_board_str = urlencode(substr($board, 0, $url_index) . "X" . substr($board, $url_index)); // Encode spaces for the URL
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
    // Check if 'name' is present in the GET request
    if (isset($_GET['name']) && !empty($_GET['name'])) {
        // Get the 'name' from the query string
        $name = htmlspecialchars($_GET['name']); // Sanitize for security
        // Get the current date
        date_default_timezone_set('America/New_York');
        $date = date('m/d/y, h:i A'); // Example: "Saturday, September 14, 2024"

        if (isset($_GET['board'])) {
            $board = str_replace('%20', ' ', $_GET['board']); // Decode spaces from URL
        } else {
            $board = '        '; // 9 spaces for an empty board
        }

        // Display the greeting
        echo "
        <div class='form_box'>
        <h1>Hello, $name!</h1>
        <p>Today's date is $date.</p>
        ";
        // Display the Tic-Tac-Toe board
        display_board($board, $name);
        echo '</div>';
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