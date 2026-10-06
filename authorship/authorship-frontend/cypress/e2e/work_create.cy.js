describe('Flujo de Registro de Obras', () => {
    const token = 'test-token-author-xyz';
    const authorUser = {
        id: 10,
        username: 'elena_art',
        email: 'elena.vazquez@example.com',
        role: 'author'
    };

    const plans = [
        { id: 1, name: 'Básico', points: 30 },
        { id: 2, name: 'Creador', points: 50 }
    ];

    beforeEach(() => {
        cy.window().then((win) => {
            win.localStorage.setItem('token', token);
        });

        cy.intercept('GET', '**/api/users/me/', {
            statusCode: 200,
            body: authorUser
        }).as('getUserMe');

        cy.intercept('GET', '**/api/subscriptions/plans/', {
            statusCode: 200,
            body: plans
        }).as('getPlans');

        cy.intercept('GET', '**/api/users/notifications/', {
            statusCode: 200,
            body: []
        }).as('getNotifications');
    });

    describe('Formulario de Libro', () => {
        beforeEach(() => {
            cy.visit('/works/create?type=book');
            cy.wait(['@getUserMe', '@getPlans']);
        });

        it('muestra los campos específicos de Libro', () => {
            cy.contains('.nav-user', 'elena_art').should('be.visible');
            cy.contains('h1', 'Registrar Libro').should('be.visible');

            cy.get('input[placeholder="Ej: 320"]').should('be.visible');
            cy.get('input[placeholder="Ej: 978-84-123456-7-8"]').should('be.visible');
            cy.contains('label', 'Idioma').should('be.visible');
        });

        it('sube una obra correctamente', () => {
            cy.intercept('POST', '**/api/works/', {
                statusCode: 201,
                body: {
                    id: 50,
                    title: 'El enigma de las sombras',
                    status: 'approved'
                }
            }).as('createWork');

            cy.get('#title').type('El enigma de las sombras');
            cy.get('#description').type('Una novela de misterio ambientada en una ciudad costera donde una serie de manuscritos olvidados desvelan un secreto centenario.');

            cy.get('select.custom-select').first().select('1');

            cy.get('input[type="number"][placeholder="Ej: 320"]').type('284');
            cy.get('input[placeholder="Ej: 978-84-123456-7-8"]').type('978-84-123456-7-8');
            cy.get('.grid-4-cols select').first().select('Misterio / Suspense');
            cy.get('select.select-pink').select('Español');

            cy.get('.hidden-file-input').first().selectFile({
                contents: Cypress.Buffer.from('Contenido obra principal'),
                fileName: 'novela_el_enigma.pdf',
                mimeType: 'application/pdf'
            }, { force: true });

            cy.get('.hidden-file-input').last().selectFile({
                contents: Cypress.Buffer.from('Resumen de los primeros capítulos'),
                fileName: 'resumen.pdf',
                mimeType: 'application/pdf'
            }, { force: true });

            cy.get('.license-card select').select('by-nc');
            cy.contains('.preview-text', 'Permite crear obras derivadas pero nunca para beneficio económico.').should('be.visible');

            cy.get('.btn-save').click();

            cy.wait('@createWork').its('response.statusCode').should('eq', 201);

            cy.get('.popup-notification')
                .should('be.visible')
                .and('contain', '¡Obra registrada y protegida con éxito!');

            cy.url({ timeout: 6000 }).should('include', '/dashboard');
        });

        it('muestra aviso preventivo cuando la IA rechaza el contenido pero se solicitó revisión manual', () => {
            cy.intercept('POST', '**/api/works/', {
                statusCode: 201,
                body: {
                    id: 51,
                    status: 'appealed',
                    rejection_reason: 'Detectada posible infracción en el análisis de texto.'
                }
            }).as('createWorkRejected');

            cy.get('#title').type('Obra con Texto en Conflicto');
            cy.get('#description').type('Una novela de misterio ambientada en una ciudad costera donde una serie de manuscritos olvidados desvelan un secreto centenario.');
            cy.get('input[type="number"][placeholder="Ej: 320"]').type('284');
            cy.get('input[placeholder="Ej: 978-84-123456-7-8"]').type('978-84-123456-7-8');
            cy.get('.grid-4-cols select').first().select('Misterio / Suspense');
            cy.get('select.select-pink').select('Español');

            cy.get('.hidden-file-input').first().selectFile({
                contents: Cypress.Buffer.from('Contenido polémico'),
                fileName: 'novela_el_enigma.pdf',
                mimeType: 'application/pdf'
            }, { force: true });

            cy.get('.hidden-file-input').last().selectFile({
                contents: Cypress.Buffer.from('Resumen de los primeros capítulos'),
                fileName: 'resumen.pdf',
                mimeType: 'application/pdf'
            }, { force: true });

            cy.get('.btn-save').click();
            cy.wait('@createWorkRejected');

            cy.get('.popup-notification.warning')
                .should('be.visible')
                .and('contain', 'El sistema de validación por IA ha rechazado tu obra')
                .and('contain', 'revisión manual');
        });
    });

    describe('Formulario de Música', () => {
        it('muestra los campos específicos para proyectos de música', () => {
            cy.visit('/works/create?type=music');
            cy.wait(['@getUserMe', '@getPlans']);

            cy.contains('h1', 'Registrar Música').should('be.visible');
            cy.contains('label', 'Duración (minutos)').should('be.visible');
            cy.get('.grid-3-cols select').should('be.visible');
            cy.contains('label', 'Álbum').should('be.visible');
            cy.get('.grid-3-cols select').should('be.visible');
            cy.get('input[placeholder="Ej: Nombre del álbum"]').should('be.visible');
            cy.contains('label', 'Género').should('be.visible');
            cy.get('.grid-3-cols select').should('be.visible');
        });
    });

    describe('Formulario de Vídeos', () => {
        it('muestra los campos específicos para proyectos de vídeo', () => {
            cy.visit('/works/create?type=video');
            cy.wait(['@getUserMe', '@getPlans']);

            cy.contains('h1', 'Registrar Vídeo').should('be.visible');
            cy.contains('label', 'Duración (minutos)').should('be.visible');
            cy.contains('label', 'Categoría').should('be.visible');
            cy.get('.grid-2-cols select').should('be.visible');
        });
    });


    describe('Formulario de Software', () => {
        it('muestra los campos específicos para proyectos de software', () => {
            cy.visit('/works/create?type=software');
            cy.wait(['@getUserMe', '@getPlans']);

            cy.contains('h1', 'Registrar Software').should('be.visible');
            cy.get('input[placeholder="Ej: Python, TypeScript..."]').should('be.visible');
            cy.get('input[placeholder="https://github.com/..."]').should('be.visible');
            cy.get('input[placeholder="https://docs...."]').should('be.visible');
        });
    });

    describe('Formulario de Pintura', () => {
        it('muestra los campos específicos para proyectos de pintura', () => {
            cy.visit('/works/create?type=paint');
            cy.wait(['@getUserMe', '@getPlans']);

            cy.contains('h1', 'Registrar Pintura').should('be.visible');
            cy.contains('label', 'Altura (cm)').should('be.visible');
            cy.contains('label', 'Peso (kg)').should('be.visible');
            cy.contains('label', 'Material / Técnica ').should('be.visible');
            cy.get('.grid-3-cols select').should('be.visible');
        });
    });

    describe('Formulario de Escultura', () => {
        it('muestra los campos específicos para proyectos de escultura', () => {
            cy.visit('/works/create?type=sculpture');
            cy.wait(['@getUserMe', '@getPlans']);

            cy.contains('h1', 'Registrar Escultura').should('be.visible');
            cy.contains('label', 'Altura (cm)').should('be.visible');
            cy.contains('label', 'Peso (kg)').should('be.visible');
            cy.contains('label', 'Material / Técnica ').should('be.visible');
            cy.get('.grid-3-cols select').should('be.visible');
        });
    });

    describe('Control de sesión desde el navbar', () => {
        it('muestra el pop up de confirmación al pulsar "Cerrar Sesión"', () => {
            cy.visit('/works/create?type=book');
            cy.wait(['@getUserMe', '@getPlans']);

            cy.get('.btn-logout').click();

            cy.get('.popup-notification')
                .should('be.visible')
                .and('contain', '¿Estás seguro de que deseas cerrar sesión?');

            cy.get('.btn-cancel').click();
            cy.get('.popup-notification').should('not.exist');
            cy.url().should('include', '/works/create');
        });
    });
});