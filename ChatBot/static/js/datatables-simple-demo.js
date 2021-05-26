window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesSimple = document.getElementById('datatablesSimple');
    const datatable = document.getElementById('datatableHistory')
    if (datatablesSimple) {
        new simpleDatatables.DataTable(datatablesSimple);
    }
    if (datatable) {
        new simpleDatatables.DataTable(datatable);
    }
});
