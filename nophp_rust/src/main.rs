use pyo3::{prelude::*, types::PyTuple};
use std::env;

fn main() -> PyResult<()> {
    let args: Vec<String> = env::args().collect();

    let py_foo = include_str!(concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../lang/lexer.py"
    ));
    let py_app = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/../lang/lexer.py"));
    let from_python = Python::with_gil(move |py| -> PyResult<Py<PyAny>> {
        PyModule::from_code(py, py_foo, "lexer", "lexer")?;
        let app: Py<PyAny> = PyModule::from_code(py, py_app, "", "")?
            .getattr("run")?
            .into();
        app.call1(py, PyTuple::new(py, vec![args[1].clone()]))
    });

    println!("py: {}", from_python?);
    Ok(())
}
