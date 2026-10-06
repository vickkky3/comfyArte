describe('Panel Principal', () => {
    const token = 'valid-session-token-xyz';

    const consumer = {
        id: 10,
        username: 'carlos_reader',
        email: 'carlos@example.com',
        first_name: 'Carlos',
        last_name: 'Navarro',
        role: 'consumer',
        interests: 'book,music'
    };

    const author = {
        id: 20,
        username: 'elena_art',
        email: 'elena@example.com',
        first_name: 'Elena',
        last_name: 'Vázquez',
        role: 'author',
        biography: 'Escritora e ilustradora digital con experiencia en narrativa de ficción y diseño conceptual.'
    };

    const activeSubscription = {
        plan_name: 'Plan Creador',
        end_date: '2026-12-31T23:59:59Z'
    };

    const authorWorks = [
        {
            id: 101,
            title: 'El enigma de las sombras',
            work_type: 'book',
            status: 'published'
        },
        {
            id: 102,
            title: 'Ecos del Atardecer',
            work_type: 'music',
            status: 'approved'
        }
    ];

    const recommendedWorks = [
        {
            id: 201,
            title: 'Luces y Sombras Urbanas',
            work_type: 'book'
        },
        {
            id: 202,
            title: 'Suspendido',
            work_type: 'music'
        }
    ];

    const subscribedAuthors = [
        {
            id: 1,
            username: 'lucia_beats',
            first_name: 'Lucía',
            last_name: 'Navarro'
        }
    ];

    const savedWorks = [
        {
            id: 301,
            title: 'Luz Quebrada sobre Óleo',
            work_type: 'book'
        }
    ];

    beforeEach(() => {
        cy.intercept('GET', '**/api/users/notifications/', { statusCode: 200, body: [] }).as('getNotifications');
    });


    describe('Vista de Consumidor', () => {
        beforeEach(() => {
            cy.intercept('GET', '**/api/users/me/', { statusCode: 200, body: consumer }).as('getUserMe');
            cy.intercept('GET', '**/api/subscriptions/points/', { statusCode: 200, body: { points: 150 } }).as('getPoints');
            cy.intercept('GET', '**/api/subscriptions/me/', { statusCode: 200, body: activeSubscription }).as('getMySubscription');
            cy.intercept('GET', '**/api/subscriptions/authors/subscribe/', { statusCode: 200, body: subscribedAuthors }).as('getSubscribedAuthors');
            cy.intercept('GET', '**/api/subscriptions/works/subscribe/', { statusCode: 200, body: savedWorks }).as('getSavedWorks');
            cy.intercept('GET', '**/api/works/recommended/', { statusCode: 200, body: recommendedWorks }).as('getRecommendedWorks');

            cy.visit('/dashboard', {
                onBeforeLoad(win) {
                    win.localStorage.setItem('token', token);
                }
            });

            cy.wait(['@getUserMe', '@getPoints', '@getMySubscription', '@getSubscribedAuthors', '@getSavedWorks', '@getRecommendedWorks']);
        });

        it('muestra la interfaz de consumidor', () => {
            cy.contains('.consumer-badges .points', 'Plan Creador').should('be.visible');
            cy.contains('.consumer-badges .points', '150 Puntos').should('be.visible');

            cy.contains('.role-badge', 'CONSUMIDOR').should('be.visible');
            cy.contains('.profile-name', 'Carlos Navarro').should('be.visible');
            cy.contains('.username-text', '@carlos_reader').should('be.visible');

            cy.contains('.badge-interes', 'LIBRO').should('be.visible');
            cy.contains('.badge-interes', 'MÚSICA').should('be.visible');

            cy.contains('.sidebar-nav-list', 'Catálogo de Obras/Autores').should('be.visible');
            cy.contains('.sidebar-nav-list', 'Obras Guardadas').should('be.visible');

            cy.contains('.header-text h1', 'Catálogo de Obras').should('be.visible');
            cy.contains('.recommended-table', 'Luces y Sombras Urbanas').should('be.visible');
            cy.contains('.recommended-table', 'Suspendido').should('be.visible');

            cy.contains('.card-section', 'Mis autores').within(() => {
                cy.contains('.author-name', 'Lucía Navarro').should('be.visible');
            });
            cy.contains('.card-section', 'Obras Guardadas').within(() => {
                cy.contains('.saved-work-title', 'Luz Quebrada sobre Óleo').should('be.visible');
            });
        });

        it('permite editar el perfil del consumidor', () => {
            cy.intercept('PATCH', '**/api/users/me/', {
                statusCode: 200,
                body: {
                    ...consumer,
                    first_name: 'Carlos López',
                    interests: 'book,video'
                }
            }).as('updateProfile');

            cy.get('.btn-outline-edit').click();

            cy.get('input[placeholder="Nombre"]').clear().type('Carlos López');

            cy.get('.interest-option').contains('VIDEO').click();

            cy.get('.btn-save-action').click();
            cy.get('.popup-notification').should('be.visible');
            cy.get('.btn-confirm').click();

            cy.wait('@updateProfile');
            cy.contains('.profile-name', 'Carlos López').should('be.visible');
        });
    });

    describe('Vista de Autor', () => {
        beforeEach(() => {
            cy.intercept('GET', '**/api/users/me/', { statusCode: 200, body: author }).as('getUserMe');
            cy.intercept('GET', '**/api/subscriptions/authors/stats/', {
                statusCode: 200,
                body: { subscribers_count: 8, saved_works_count: 24 }
            }).as('getAuthorStats');
            cy.intercept('GET', `**/api/works/authors/${author.id}/`, {
                statusCode: 200,
                body: authorWorks
            }).as('getAuthorWorks');

            cy.visit('/dashboard', {
                onBeforeLoad(win) {
                    win.localStorage.setItem('token', token);
                }
            });

            cy.wait(['@getUserMe', '@getAuthorStats', '@getAuthorWorks']);
        });

        it('muestra la interfaz de autor', () => {
            cy.contains('.role-badge', 'AUTOR').should('be.visible');
            cy.get('.consumer-badges').should('not.exist');
            cy.contains('.bio-text', 'Escritora e ilustradora digital con experiencia en narrativa de ficción y diseño conceptual.').should('be.visible');

            cy.contains('.sidebar-nav-list', 'Registrar libro').should('be.visible');
            cy.contains('.sidebar-nav-list', 'Registrar música').should('be.visible');
            cy.contains('.sidebar-nav-list', 'Registrar vídeo').should('be.visible');
            cy.contains('.sidebar-nav-list', 'Registrar software').should('be.visible');
            cy.contains('.sidebar-nav-list', 'Registrar pintura').should('be.visible');
            cy.contains('.sidebar-nav-list', 'Registrar escultura').should('be.visible');

            cy.contains('.stat-label', 'Suscriptores').parent().contains('.stat-number', '8');
            cy.contains('.stat-label', 'Obras en favoritos').parent().contains('.stat-number', '24');
            cy.contains('.stat-label', 'Obras publicadas').parent().contains('.stat-number', '1');

            cy.contains('.recommended-table', 'El enigma de las sombras').within(() => {
                cy.contains('.status-badge', 'Publicada').should('be.visible');
            });
            cy.contains('.recommended-table', 'Ecos del Atardecer').within(() => {
                cy.contains('.status-badge', 'Aprobada').should('be.visible');
            });
        });

        it('permite eliminar una obra', () => {
            cy.intercept('DELETE', '**/api/works/101/', { statusCode: 204, body: {} }).as('deleteWorkReq');

            cy.get('.btn-delete-plain').first().click();

            cy.get('.popup-notification')
                .should('be.visible')
                .and('contain', '¿Estás seguro de que deseas eliminar esta obra?');

            cy.get('.btn-confirm').click();

            cy.wait('@deleteWorkReq');
            cy.get('.popup-notification.success')
                .should('be.visible')
                .and('contain', 'Obra eliminada correctamente.');

            cy.contains('.recommended-table', 'El enigma de las sombras').should('not.exist');
        });

        it('permite editar la biografía profesional del autor', () => {
            cy.intercept('PATCH', '**/api/users/me/', {
                statusCode: 200,
                body: {
                    ...author,
                    biography: 'Nueva biografía.'
                }
            }).as('updateBio');

            cy.get('.btn-outline-edit').click();
            cy.get('.edit-bio-textarea').clear().type('Nueva biografía.');

            cy.get('.btn-save-action').click({ force: true });
            cy.get('.btn-confirm').click();

            cy.wait('@updateBio');
            cy.contains('.bio-text', 'Nueva biografía.').should('be.visible');
        });
    });


    describe('Cierre de Sesión', () => {
        it('solicita confirmación para cerrar sesión', () => {
            cy.intercept('GET', '**/api/users/me/', { statusCode: 200, body: consumer });
            cy.intercept('GET', '**/api/subscriptions/**', { statusCode: 200, body: [] });
            cy.intercept('GET', '**/api/works/**', { statusCode: 200, body: [] });

            cy.visit('/dashboard', {
                onBeforeLoad(win) {
                    win.localStorage.setItem('token', token);
                }
            });

            cy.get('.btn-logout').click();

            cy.get('.popup-notification')
                .should('be.visible')
                .and('contain', '¿Estás seguro de que deseas cerrar sesión?');

            cy.get('.btn-confirm').click();

            cy.url().should('include', '/login');
            cy.window().then((win) => {
                expect(win.localStorage.getItem('token')).to.be.null;
            });
        });
    });
});