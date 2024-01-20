<?php
namespace App;

class BlaBla {
    private $a;
    private function test() {
        $this->a = "a";
    }
    public function ptest() {
        $this->test();
        return $this->a;
    }
}

$bla = new BlaBla();
echo $bla->ptest();
echo $bla->a;

// Styling will be in the styles.php file
require_once("config/styles.php");

// For automatic dark mode
echo <html data-bs-theme="dark">;

// Head
//  Let's add bootstrap styles
echo 
<head>
    $BOOTSTRAP 
</head>;

// Body
//  We can also use the variables to interact with HTML
$PCLASS = "lead";
echo 
<body>
    <h1> "This is a title" </h1>
    .<p class=$PCLASS> "This is a lead" </p> // dot allows us to join multiple statements together
    .<a href="/store"> "Go to Store" </a>
</body>;


// Run with: python -m nophp config/wool.yaml
?>