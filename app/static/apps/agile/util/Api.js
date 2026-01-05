Ext.define('AgileAcpt.util.Api', {
    singleton: true,
    apiBase: '/api',
    init: function () {
        Ext.Ajax.on('requestexception', function (conn, response) {
            if (response.status === 401) {
                localStorage.removeItem('jwt');
                Ext.Msg.alert('Session Expired', 'Please login again.', function () {
                    window.location = '/login.html';
                });
            }
        });
    }
});
