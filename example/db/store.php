<?php
namespace Shops;

class Shop {
    private items;
    private conn;

    public function __construct($items) {
        $this->items = $items;
        $this->conn = sql_connect("db.sql");
    }

    public function sell($item) {
        /// ... bla bla bla bla bla bla bla bla bla bla
    }
}
?>