Ext.application({
  name: "AgileAcpt",
  appFolder: "/apps/agile",
  requires: ["AgileAcpt.util.Api", "AgileAcpt.view.login.Login", "AgileAcpt.view.main.Main"],
  launch: function () {
    AgileAcpt.util.Api.init();
    var token = localStorage.getItem("jwt");
    if (token) {
      Ext.Ajax.setDefaultHeaders({ Authorization: "Bearer " + token });
      Ext.create({ xtype: "mainview" });
    } else {
      window.location.href = "/login";
    }
  },
});
