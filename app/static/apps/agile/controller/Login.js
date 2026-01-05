Ext.define("AgileAcpt.controller.Login", {
  extend: "Ext.app.ViewController",
  alias: "controller.login",

  onLoginClick: function (btn) {
    var form = btn.up("form").getForm();
    if (form.isValid()) {
      var values = form.getValues();
      Ext.Ajax.request({
        url: "/api/auth/login",
        method: "POST",
        jsonData: values,
        success: function (response) {
          var data = Ext.decode(response.responseText);
          localStorage.setItem("jwt", data.token);
          Ext.Ajax.setDefaultHeaders({ Authorization: "Bearer " + data.token });
          btn.up("window").close();
          Ext.create({ xtype: "mainview" });
        },
        failure: function (response) {
          var msg = "Login failed";
          try {
            var data = Ext.decode(response.responseText);
            msg = data.error || msg;
          } catch (e) {}
          Ext.Msg.alert("Error", msg);
        },
      });
    }
  },
});
