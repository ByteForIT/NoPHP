use pyo3::prelude::*;

fn main() -> PyResult<()> {
    let py_foo = include_str!(concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../lang/lexer.py"
    ));
    let py_app = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/../lang/lexer.py"));
    let from_python = Python::with_gil(|py| -> PyResult<Py<PyAny>> {
        PyModule::from_code(py, py_foo, "lexer", "lexer")?;
        let app: Py<PyAny> = PyModule::from_code(py, py_app, "", "")?
            .getattr("run")?
            .into();
        app.call0(py)
    });

    println!("py: {}", from_python?);
    Ok(())
}
