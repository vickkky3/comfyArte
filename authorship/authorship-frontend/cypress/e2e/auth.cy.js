describe('Flujo de Bienvenida y Selección de Rol', () => {
    beforeEach(() => {
        cy.visit('/');
    });

    it('muestra correctamente el título y ambas tarjetas de rol', () => {
        cy.contains('h1', 'BIENVENIDO A LA PLATAFORMA').should('be.visible');
        cy.contains('ComfyARTE').should('be.visible');

        cy.contains('.card', 'Soy Autor')
            .should('be.visible')
            .and('contain', 'Registrarme como Creador');

        cy.contains('.card', 'Soy Consumidor')
            .should('be.visible')
            .and('contain', 'Registrarme como Consumidor');

        cy.contains('.login-link', 'Inicia sesión aquí').should('be.visible');
    });

    it('navega al formulario de registro de autor al pulsar la tarjeta de Autor', () => {
        cy.contains('.card', 'Soy Autor').click();

        cy.url().should('include', '/register/author');
    });

    it('navega al formulario de registro de consumidor al pulsar la tarjeta de Consumidor', () => {
        cy.contains('.card', 'Soy Consumidor').click();

        cy.url().should('include', '/register/consumer');
    });

    it('redirige a la vista de login al pulsar en el enlace inferior', () => {
        cy.contains('.login-link a', 'Inicia sesión aquí').click();

        cy.url().should('include', '/login');
    });
});

describe('Flujo de Registro de Usuarios (Autor y Consumidor)', () => {

    describe('Registro de Autor (/register/author)', () => {
        beforeEach(() => {
            cy.visit('/register/author');
        });

        it('muestra la interfaz de autor', () => {
            cy.contains('h1.register', 'Registro de Autor').should('be.visible');
            cy.contains('.role-highlight', 'autor').should('be.visible');
            cy.contains('Protege tu creatividad').should('be.visible');

            cy.get('#biography').should('be.visible');
            cy.get('.interests-grid').should('not.exist');
        });

        it('permite registrar un autor con éxito y redirige a dashboard', () => {
            const semilla = Date.now();
            const newAuthor = {
                first_name: 'Elena',
                last_name: 'Vázquez',
                username: `elena_${semilla}`,
                email: `elena_${semilla}@example.com`,
                password: 'TFGTest2026!',
                biography: 'Escritora e ilustradora digital con experiencia en narrativa de ficción y diseño conceptual.'
            };

            cy.intercept('POST', '**/api/users/register/').as('registerAuthor');

            cy.get('#first_name').type(newAuthor.first_name);
            cy.get('#last_name').type(newAuthor.last_name);
            cy.get('#username').type(newAuthor.username);
            cy.get('#email').type(newAuthor.email);
            cy.get('#password').type(newAuthor.password);
            cy.get('#biography').type(newAuthor.biography);

            cy.get('.btn-register').click();

            cy.wait('@registerAuthor').then((interception) => {
                expect(interception.response.statusCode).to.equal(201);
                expect(interception.request.body.role).to.equal('author');
                expect(interception.request.body.biography).to.equal(newAuthor.biography);
            });

            cy.url().should('include', '/dashboard');
            cy.window().then((win) => {
                expect(win.localStorage.getItem('token')).to.be.a('string');
            });
        });

        it('muestra el popup de error cuando Django rechaza un campo (ej. usuario duplicado)', () => {
            cy.intercept('POST', '**/api/users/register/', {
                statusCode: 400,
                body: {
                    username: ['El nombre de usuario ya está en uso. Por favor, elige otro.']
                }
            }).as('registerDuplicateUser');

            cy.get('#first_name').type('Lucía');
            cy.get('#last_name').type('Navarro');
            cy.get('#username').type('lucia_beats');
            cy.get('#email').type('lucia@example.com');
            cy.get('#password').type('TFGTest2026!');

            cy.get('.btn-register').click();
            cy.wait('@registerDuplicateUser');

            cy.get('.popup-notification.error')
                .should('be.visible')
                .and('contain', 'Operación Denegada')
                .and('contain', 'El nombre de usuario ya está en uso');

            cy.get('.popup-close').click();
            cy.get('.popup-notification').should('not.exist');
        });
    });

    describe('Registro de Consumidor (/register/consumer)', () => {
        beforeEach(() => {
            cy.visit('/register/consumer');
        });

        it('muestra la interfaz de consumidor con intereses', () => {
            cy.contains('h1.register', 'Registro de Consumidor').should('be.visible');
            cy.contains('.role-highlight', 'consumidor').should('be.visible');
            cy.contains('Descubre talento único').should('be.visible');

            cy.get('.interests-grid').should('be.visible');
            cy.get('#biography').should('not.exist');
        });

        it('permite registrar un consumidor seleccionando intereses', () => {
            const semilla = Date.now();
            const newConsumer = {
                first_name: 'Carlos',
                last_name: 'Navarro',
                username: `carlos_${semilla}`,
                email: `carlos_${semilla}@example.com`,
                password: 'TFGTest2026!'
            };

            cy.intercept('POST', '**/api/users/register/').as('registerConsumer');

            cy.get('#first_name').type(newConsumer.first_name);
            cy.get('#last_name').type(newConsumer.last_name);
            cy.get('#username').type(newConsumer.username);
            cy.get('#email').type(newConsumer.email);
            cy.get('#password').type(newConsumer.password);

            cy.get('input[type="checkbox"][value="book"]').check();
            cy.get('input[type="checkbox"][value="paint"]').check();

            cy.get('.btn-register').click();

            cy.wait('@registerConsumer').then((interception) => {
                expect(interception.response.statusCode).to.equal(201);
                expect(interception.request.body.role).to.equal('consumer');
                expect(interception.request.body.interests).to.include('book');
                expect(interception.request.body.interests).to.include('paint');
            });

            cy.url().should('include', '/dashboard');
        });
    });

    describe('Navegación de retorno', () => {
        it('el botón "Volver" regresa a la pantalla raíz', () => {
            cy.visit('/register/author');
            cy.get('.btn-back-top').click();
            cy.url().should('eq', `${Cypress.config().baseUrl}/`);
        });
    });

});

describe('Flujo de Inicio de Sesión (Login)', () => {
    beforeEach(() => {
        cy.clearLocalStorage();
        cy.visit('/login');
    });

    it('muestra correctamente el formulario de login', () => {
        cy.contains('h1', 'Identificación').should('be.visible');
        cy.get('input[type="text"][placeholder="Tu usuario..."]').should('be.visible');
        cy.get('input[type="password"][placeholder="Tu contraseña..."]').should('be.visible');
        cy.get('button[type="submit"].btn-login').should('be.visible').and('contain', 'Iniciar Sesión');
        cy.contains('.back-link a', 'Regístrate como autor o consumidor').should('be.visible');
    });

    it('inicia sesión con credenciales válidas y se mantiene en el dashboard', () => {
        const semilla = Date.now();
        const testUser = {
          username: `lucas_${semilla}`,
          password: 'TFGTest2026!',
          email: `lucas_${semilla}@example.com`,
          first_name: 'Lucas',
          last_name: 'Lopez',
          role: 'consumer'
        };
      
        cy.request('POST', 'http://localhost:8000/api/users/register/', testUser);
      
        cy.intercept('POST', '**/api/users/login/').as('loginRequest');
      
        cy.get('input[type="text"][placeholder="Tu usuario..."]').type(testUser.username);
        cy.get('input[type="password"][placeholder="Tu contraseña..."]').type(testUser.password);
        cy.get('button[type="submit"].btn-login').click();
      
        cy.wait('@loginRequest').its('response.statusCode').should('eq', 200);
      
        cy.url().should('include', '/dashboard');
      });

    it('muestra popup de error al ingresar credenciales incorrectas', () => {
        cy.intercept('POST', '**/api/users/login/', {
            statusCode: 400,
            body: { detail: 'Credenciales inválidas. Comprueba tu usuario y contraseña.' }
        }).as('loginFailed');

        cy.get('input[type="text"][placeholder="Tu usuario..."]').type('usuario_inexistente');
        cy.get('input[type="password"][placeholder="Tu contraseña..."]').type('TFGTest');
        cy.get('button[type="submit"].btn-login').click();

        cy.wait('@loginFailed');

        cy.get('.popup-notification.error')
            .should('be.visible')
            .and('contain', 'Operación Denegada')
            .and('contain', 'Credenciales inválidas');

        cy.url().should('include', '/login');
        cy.window().then((win) => {
            expect(win.localStorage.getItem('token')).to.be.null;
        });

        cy.get('.popup-close').click();
        cy.get('.popup-notification').should('not.exist');
    });

    it('navega a la raíz al pulsar en el enlace de registro', () => {
        cy.contains('.back-link a', 'Regístrate como autor o consumidor').click();
        cy.url().should('eq', `${Cypress.config().baseUrl}/`);
    });
});