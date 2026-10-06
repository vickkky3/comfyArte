Cypress.Commands.add('loginAsConsumer', (token = 'token_test_consumer') => {
    cy.window().then((win) => {
      win.localStorage.setItem('token', token);
      win.localStorage.setItem('role', 'Consumer');
      win.localStorage.setItem('user', JSON.stringify({ username: 'carlos_reader', role: 'Consumer' }));
    });
  });
  
  Cypress.Commands.add('loginAsAuthor', (token = 'token_test_author') => {
    cy.window().then((win) => {
      win.localStorage.setItem('token', token);
      win.localStorage.setItem('role', 'Author');
      win.localStorage.setItem('user', JSON.stringify({ username: 'autor1', role: 'Author' }));
    });
  });