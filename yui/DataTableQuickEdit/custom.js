YUI({
//	filter: 'raw', combine: false,
	gallery: 'gallery-2013.06.26-23-09'
}).use(
	'datatable-datasource',
	'gallery-quickedit',
	'gallery-paginator',
function(Y) {
"use strict";

	function sendRequest()
	{
		table.datasource.load(
		{
			request: pg.getState()
		});
	}

// Raw data

	var data =
	[
		{id:'n1', year:1950, quantity:10, title:"The Lion, the Witch and the Wardrobe"},
		{id:'n2', year:1951, quantity:5, title:"Prince Caspian: The Return to Narnia"},
		{id:'n3', year:1952, quantity:2, title:"The Voyage of the Dawn Treader"},
		{id:'n4', year:1953, quantity:6, title:"The Silver Chair"},
		{id:'n5', year:1954, quantity:9, title:"The Horse and His Boy"},
		{id:'n6', year:1955, quantity:4, title:"The Magician's Nephew"},
		{id:'n7', year:1956, quantity:8, title:"The Last Battle"},
		{id:'lsf1', year:1938, quantity:10, title:"Out of the Silent Planet"},
		{id:'lsf2', year:1943, quantity:5, title:"Perelandra"},
		{id:'lsf3', year:1945, quantity:2, title:"That Hideous Strength"},
		{id:'p1', year:1995, quantity:7, title:"Northern Lights"},
		{id:'p2', year:1997, quantity:5, title:"The Subtle Knife"},
		{id:'p3', year:2000, quantity:8, title:"The Amber Spyglass"},
		{id:'t0', year:1937, quantity:5, title:"The Hobbit"},
		{id:'t1', year:1955, quantity:12, title:"The Fellowship of the Ring"},
		{id:'t2', year:1955, quantity:0, title:"The Two Towers"},
		{id:'t3', year:1955, quantity:8, title:"The Return of the King"},
		{id:'pd', year:1966, quantity:5, title:"Do Androids Dream of Electric Sheep?"},
		{id:'h1', year:1959, quantity:4, title:"Starship Troopers"},
		{id:'h2', year:1961, quantity:7, title:"Stranger in a Strange Land"},
		{id:'h3', year:1966, quantity:3, title:"The Moon Is a Harsh Mistress"},
		{id:'v1', year:1946, quantity:3, title:"Slan"},
		{id:'v2', year:1950, quantity:5, title:"The Voyage of the Space Beagle"},
		{id:'v3', year:1970, quantity:8, title:"Quest for the Future"},
		{id:'d1', year:1859, quantity:5, title:"On the Origin of Species by Means of Natural Selection, or the Preservation of Favoured Races in the Struggle for Life"},
		{id:'d2', year:1881, quantity:2, title:"The Formation of Vegetable Mould through the Action of Worms"},
		{id:'e1', year:1905, quantity:8, title:"On a Heuristic Viewpoint Concerning the Production and Transformation of Light"},
		{id:'e2', year:1905, quantity:5, title:"On the Electrodynamics of Moving Bodies"},
		{id:'e3', year:1917, quantity:7, title:"Kosmologische Betrachtungen zur allgemeinen Relativit&auml;tstheorie"},
		{id:'e4', year:1935, quantity:3, title:"Can Quantum-Mechanical Description of Physical Reality Be Considered Complete?"},
		{id:'g1', year:1610, quantity:5, title:"Sidereus Nuncius"},
		{id:'g2', year:1615, quantity:2, title:"Letter to the Grand Duchess Christina"},
		{id:'g3', year:1632, quantity:6, title:"Dialogo sopra i due massimi sistemi del mondo"},
		{id:'i1', year:1671, quantity:7, title:"Method of Fluxions"},
		{id:'i2', year:1687, quantity:4, title:"Philosophi&aelig; Naturalis Principia Mathematica"},
		{id:'i3', year:1704, quantity:3, title:"Opticks"}
	];

// Data Source

	// extend local data source to understand pagination

	function CustomDataSource()
	{
		CustomDataSource.superclass.constructor.apply(this, arguments);
	}

	CustomDataSource.NAME = "customdatasource";

	Y.extend(CustomDataSource, Y.DataSource.Local,
	{
		_defDataFn: function(e)
		{
			var response =
			{
				results: e.data.slice(e.request.recordOffset, e.request.recordOffset + e.request.rowsPerPage),
				meta:
				{
					totalRecords: data.length
				}
			};

			this.fire("response", Y.mix({response: response}, e));
		}
	});

	// create data source

	var ds = new CustomDataSource({source: data});

// Paginator

	var pg = new Y.Paginator(
	{
		totalRecords: 15,
		rowsPerPage: 15,
		template: '{FirstPageLink}{PreviousPageLink}{PageLinks}{NextPageLink}{LastPageLink} <span class="rpp">Rows per page:</span> {RowsPerPageDropdown}',
		rowsPerPageOptions:    [15, 30],
		firstPageLinkLabel:    '|&lt;',
		previousPageLinkLabel: '&lt;',
		nextPageLinkLabel:     '&gt;',
		lastPageLinkLabel:     '&gt;|'
	});
	pg.render('#pg');

	pg.on('changeRequest', function(state)
	{
		this.setPage(state.page, true);
		this.setRowsPerPage(state.rowsPerPage, true);
		sendRequest();
	});

	ds.on('response', function(e)
	{
		pg.setTotalRecords(e.response.meta.totalRecords, true);
		pg.render();
	});

// DataTable

	var cols =
	[
		{ key: 'title', label: 'Title', quickEdit: true },
		{ key: 'year', label: 'Year' },
		{ key: 'quantity', label: 'Quantity',
			quickEdit:
			{
				copyDown:   true,
				validation: { css: 'yiv-required yiv-integer:[0,]' }
			}
		}
	];

	var table = new Y.DataTable({columns: cols});
	table.plug(Y.Plugin.DataTableDataSource, {datasource: ds});
	table.plug(Y.Plugin.DataTableQuickEdit, {changesAlwaysInclude: ['id']});

	table.render("#table");

	sendRequest();

// Controls

	var edit  = Y.one('#edit');
	var save   = Y.one('#save');
	var cancel = Y.one('#cancel');

	edit.on('click', function()
	{
		table.qe.start();
		edit.set('disabled', true);
		save.show();
		cancel.show();
		pg.disable();
	});

	function finish()
	{
		table.qe.cancel();
		edit.set('disabled', false);
		save.hide();
		cancel.hide();
		pg.enable();
	}

	save.on('click', function()
	{
		var changes = table.qe.getChanges();
		if (changes)
		{
			if (window.console && window.console.log)
			{
				console.log(changes);
			}

			for (var i=0; i<changes.length; i++)
			{
				var change = changes[i];
				var rec    = null;
				for (var j=0; j<data.length; j++)
				{
					if (data[j].id === change.id)
					{
						rec = data[j];
						break;
					}
				}

				if (rec)
				{
					for (var key in change)
					{
						if (change.hasOwnProperty(key))
						{
							rec[key] = change[key];
						}
					}
				}
			}

			sendRequest();

			finish();
		}
	});

	cancel.on('click', function ()
	{
		finish();
	});
});
