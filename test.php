<?php

namespace App;

class Router {
    public function __construct() {
        echo "Im init!";
        echo '<br>';
    }
    public function myFunction() : int {
        echo "Hello from inside myFunction in class Router!";
        echo '<br>';
        $returns = 10; 
        return $returns;
    }
}

function RunTests($id) : void {
    $hello = "Hello ";    

    $example_html = '<h1>' . $hello . "World" . '</h1>';

    echo $example_html;

    echo '<code>';

    function ExampleFunction() : int {
        echo "I return: ";
        return 1;
    }

    $hi = ExampleFunction();

    echo $hi;

    echo '<br>';

    $router = new Router();
    

    $b = $router->myFunction();

    // If
    if ($b == 10) {
        echo "If works";
        echo '<br>';
    } else {
        echo "If failed";
        // ?panic;
    }

    // While
    while ($b != 10) {
        echo $b;
        $b = $b + 1;
    }
    
    $array = ["Hello", "World", "three"];

    // Foreach
    foreach ($array as $value) {
        echo $value;
        echo '<br>';
    }

echo '</code>';
}

RunTests(1);

class Robot
{
    public $greeting;
    // $greeting = "a";

    public function __construct()
    {
        $this->greeting = "Hello";
    }

	public function greet()
	{
		return $this->greeting;
	}

    public function bye() 
    {
        return 'Good bye!';
    }
    public function wrap()
    {
        echo "+++++++";
    }
}

class Android extends Robot
{
    public function __construct()
    {
        // ? debug;
        $this->greeting = "Hi!";
    }

}

// Instead of this
// debug_print_backtrace();
// Use this
// ?debug;

$robot = new Robot();
$a = $robot->greet(); // Hello
echo "Robot: " . $a . " Expected: " . $robot->greeting;
echo "</br>";


$android = new Android();
$b = $android->greet(); // Hi!
echo "Android: " . $b . " Expected: " . $android->greeting;
echo "</br>";
$android->bye(); // Good bye!

require_once("example.php");

use Example;

echo Example\greet();

class YourApp {
    public $greeting;
    public function __construct() {
        $this->greeting = "Welcome to NoPHP";
    } 
    public function welcome() {
        echo "<h1>" . $this->greeting . "</h1>";
    }
}
$app = new YourApp();
$app->welcome();
// ?debug;

?>

<p>
Hello World!!
</p>
