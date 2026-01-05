Ext.define('AgileAcpt.model.Job', {
    extend: 'Ext.data.Model',
    fields: [
        { name: 'id', type: 'string' },
        { name: 'type', type: 'string' },
        { name: 'status', type: 'string' },
        { name: 'createdAt', type: 'date', dateFormat: 'c' },
        { name: 'finishedAt', type: 'date', dateFormat: 'c' },
        { name: 'summary', type: 'string' }
    ]
});
