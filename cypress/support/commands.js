import 'cypress-file-upload';
// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... });
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... });
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... });
//
//
// -- This is will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... });
Cypress.Commands.add('login', (email, password) => {
	cy.request({
		url: '/api/method/login',
		method: 'POST',
		body: {
			usr: email,
			pwd: password
		}
	});
});

Cypress.Commands.add('fill_field', (fieldname, value, fieldtype='Data') => {
	let selector = `.form-control[data-fieldname="${fieldname}"]`;

	if (fieldtype === 'Text Editor') {
		selector = `[data-fieldname="${fieldname}"] .ql-editor[contenteditable=true]`;
	}
	if (fieldtype === 'Code') {
		selector = `[data-fieldname="${fieldname}"] .ace_text-input`;
	}

	cy.get(selector).as('input');

	if (fieldtype === 'Select') {
		return cy.get('@input').select(value);
	} else {
		return cy.get('@input').type(value, {waitForAnimations: false});
	}
});

Cypress.Commands.add('awesomebar', (text) => {
	cy.get('#navbar-search').type(`${text}{downarrow}{enter}`, { delay: 100 });
});

Cypress.Commands.add('new_form', (doctype) => {
	cy.visit(`/desk#Form/${doctype}/New ${doctype} 1`);
});

Cypress.Commands.add('go_to_list', (doctype) => {
	cy.visit(`/desk#List/${doctype}/List`);
});

Cypress.Commands.add('clear_cache', () => {
	cy.window().its('frappe').then(frappe => {
		frappe.ui.toolbar.clear_cache();
	});
});

Cypress.Commands.add('dialog', (title, fields) => {
	cy.window().then(win => {
		var d = new win.frappe.ui.Dialog({
			title: title,
			fields: fields,
			primary_action: function(){
				d.hide();
			}
		});
		d.show();
		return d;
	});
});

Cypress.Commands.add('get_open_dialog', () => {
	return cy.get('.modal:visible').last();
});

Cypress.Commands.add('hide_dialog', () => {
	cy.get_open_dialog().find('.btn-modal-close').click();
	cy.get('.modal:visible').should('not.exist');
});
