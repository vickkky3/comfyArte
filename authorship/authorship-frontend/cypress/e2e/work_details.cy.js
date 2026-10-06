describe('Flujo de Detalle y Gestión de Obra desde un Autor', () => {
    const token = 'author-token-abc-999';
    const workId = 42;

    const mockUser = {
        id: 5,
        username: 'elena_art',
        email: 'elena@example.com',
        role: 'author'
    };

    const book = {
        id: workId,
        title: 'El enigma de las sombras',
        work_type: 'book',
        author_username: 'elena_art',
        created_at: '2026-05-15T10:30:00Z',
        status: 'approved',
        description: 'Una novela de misterio ambientada en una ciudad costera donde una serie de manuscritos olvidados desvelan un secreto centenario.',
        plan_required: { id: 2, name: 'Plan Creador', points: 50 },
        pages: 284,
        isbn: '978-84-123456-7-8',
        genre: 'Misterio / Suspense',
        language: 'Español',
        resume_name: 'muestra_el_enigma.pdf',
        resume_type: 'application/pdf',
        file_name: 'el_enigma_completo.pdf',
        file_type: 'application/pdf',
        license: 'by-nc-sa',
        license_label: 'CC BY-NC-SA',
        hash_security: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    };

    beforeEach(() => {
        cy.window().then((win) => {
            win.localStorage.setItem('token', token);
        });

        cy.intercept('GET', '**/api/users/me/', {
            statusCode: 200,
            body: mockUser
        }).as('getUserMe');

        cy.intercept('GET', '**/api/subscriptions/plans/', {
            statusCode: 200,
            body: [
                { id: 1, name: 'Básico', points: 10 },
                { id: 2, name: 'Plan Creador', points: 50 }
            ]
        }).as('getPlans');

        cy.intercept('GET', '**/api/users/notifications/', {
            statusCode: 200,
            body: []
        }).as('getNotifications');

        cy.intercept('GET', '**/api/subscriptions/me*', {
            statusCode: 200,
            body: {
              plan: { name: 'Plan Creador', price: 9.99 },
              status: 'active'
            }
          }).as('getMySubscription');
    });

    it('muestra los detalles técnicos del libro', () => {
        cy.intercept('GET', `**/api/works/${workId}/`, {
            statusCode: 200,
            body: book
        }).as('getWorkDetail');

        cy.loginAsAuthor()
        cy.visit(`/worksAuthor/${workId}`);

        cy.wait(['@getUserMe', '@getWorkDetail', '@getPlans']);

        cy.contains('.nav-user', 'elena_art').should('be.visible');

        cy.contains('h1', 'El enigma de las sombras').should('be.visible');
        cy.contains('.circle-pink', 'LIBRO').should('be.visible');
        cy.contains('.info-block', 'Estado').should('contain', 'Aprobada');
        cy.contains('.info-block', 'Autor/a').should('contain', 'elena_art');
        cy.contains('.info-block2', 'Descripción').should('contain', 'Una novela de misterio ambientada en una ciudad costera');

        cy.contains('.plan-name', 'Plan Creador').should('be.visible');
        cy.contains('.circle-pink2', '50 puntos').should('be.visible');

        cy.get('.technical-sheet').within(() => {
            cy.contains('.tech-row, .technical-row', 'Páginas').should('contain', '284');
            cy.contains('.tech-row, .technical-row', 'ISBN').should('contain', '978-84-123456-7-8');
            cy.contains('.tech-row, .technical-row', 'Género').should('contain', 'Misterio / Suspense');
            cy.contains('.tech-row, .technical-row', 'Idioma').should('contain', 'Español');
        });

        cy.get('.signature-code').should('contain', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
    });

    it('permite copiar el hash', () => {
        cy.intercept('GET', `**/api/works/${workId}/`, {
            statusCode: 200,
            body: book
        }).as('getWorkDetail');

        cy.loginAsAuthor()
        cy.visit(`/worksAuthor/${workId}`);
        cy.wait('@getWorkDetail');

        cy.get('.btn-copy-signature').click();
        cy.get('.btn-copy-signature').should('have.class', 'btn-copied').and('contain', '¡Copiado!');
    });

    it('permite descargar la muestra gratuita del archivo', () => {
        cy.intercept('GET', `**/api/works/${workId}/`, {
            statusCode: 200,
            body: book
        }).as('getWorkDetail');

        cy.intercept('GET', `**/api/works/${workId}/serve-resume/`, {
            statusCode: 200,
            headers: {
                'content-disposition': 'attachment; filename="muestra_el_enigma.pdf"',
                'content-type': 'application/pdf'
            },
            body: 'Contenido PDF'
        }).as('downloadResume');

        cy.loginAsAuthor()
        cy.visit(`/worksAuthor/${workId}`);
        cy.wait('@getWorkDetail');

        cy.get('.btn-sidebar-secondary').contains('Verificar muestra').click();
        cy.wait('@downloadResume').its('response.statusCode').should('eq', 200);
    });

    it('abre el popup de confirmación para eliminar la obra', () => {
        cy.intercept('GET', `**/api/works/${workId}/`, {
            statusCode: 200,
            body: book
        }).as('getWorkDetail');

        cy.loginAsAuthor()
        cy.visit(`/worksAuthor/${workId}`);
        cy.wait('@getWorkDetail');

        cy.get('.btn-delete').click();

        cy.get('.popup-notification')
            .should('be.visible')
            .and('contain', 'Confirmar Acción')
            .and('contain', '¿Estás seguro de que deseas eliminar esta obra?');

        cy.get('.btn-cancel').click();
        cy.get('.popup-notification').should('not.exist');
        cy.url().should('include', `/worksAuthor/${workId}`);
    });

    it('elimina la obra exitosamente tras confirmar y redirige al dashboard', () => {
        cy.intercept('GET', `**/api/works/${workId}/`, {
            statusCode: 200,
            body: book
        }).as('getWorkDetail');

        cy.intercept('DELETE', `**/api/works/${workId}/`, {
            statusCode: 204,
            body: {}
        }).as('deleteWorkRequest');

        cy.loginAsAuthor()
        cy.visit(`/worksAuthor/${workId}`);
        cy.wait('@getWorkDetail');

        cy.get('.btn-delete').click();

        cy.get('.btn-confirm').click();

        cy.wait('@deleteWorkRequest').its('response.statusCode').should('eq', 204);

        cy.get('.popup-notification')
            .should('be.visible')
            .and('contain', 'Obra eliminada correctamente.');
    });
});

describe('Flujo de Detalle y Gestión de Obra desde un Consumidor', () => {
    const token = 'consumer-token-abc-999';
    const workId = 101;
    const authorId = 22;

    const consumer = {
        id: 99,
        username: 'carlos_lector',
        email: 'carlos@example.com',
        role: 'consumer'
    };

    const music = {
        id: workId,
        title: 'Ecos del Atardecer',
        work_type: 'music',
        author: authorId,
        author_username: 'elena_art',
        created_at: '2026-08-10T12:00:00Z',
        description: 'Composición ambiental instrumental producida con sintetizadores analógicos y ritmos suaves.',
        plan_required: { id: 2, name: 'Plan Creador', points: 50 },
        duration: 2.30,
        language: 'Español',
        file_name: 'ecos_del_atardecer.mp3',
        file_type: 'audio/mp3',
        resume_name: 'muestra_ecos_del_atardecer.mp3',
        resume_type: 'audio/mp3',
        license: 'by-nc',
        license_label: 'CC BY-NC',
        hash_security: 'a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890'
    };

    const authorDetails = {
        id: authorId,
        username: 'elena_art',
        first_name: 'Elena',
        last_name: 'Vázquez',
        biography: 'Escritora e ilustradora digital con experiencia en narrativa de ficción y diseño conceptual.'
    };

    const authorStats = {
        subscribers_count: 14,
        saved_works_count: 89
    };

    const authorWorks = [
        {
            id: workId,
            title: 'Ecos del Atardecer',
            work_type: 'music',
            created_at: '2026-08-10T12:00:00Z',
            status: 'published'
        },
        {
            id: 102,
            title: 'El Algoritmo Silencioso',
            work_type: 'book',
            created_at: '2026-09-01T10:00:00Z',
            status: 'published'
        }
    ];

    beforeEach(() => {
        cy.intercept('GET', '**/api/users/me/', {
            statusCode: 200,
            body: consumer
        }).as('getUserMe');

        cy.intercept('GET', '**/api/subscriptions/points/', {
            statusCode: 200,
            body: { points: 100 }
        }).as('getUserPoints');

        cy.intercept('GET', '**/api/subscriptions/plans/', {
            statusCode: 200,
            body: [
                { id: 1, name: 'Plan Básico', points: 30 },
                { id: 2, name: 'Plan Creador', points: 50 }
            ]
        }).as('getPlans');

        cy.intercept('GET', '**/api/users/notifications/', {
            statusCode: 200,
            body: []
        }).as('getNotifications');

        cy.intercept('GET', '**/api/subscriptions/authors/subscribe/', {
            statusCode: 200,
            body: []
        }).as('getSubscribedAuthors');

        cy.intercept('GET', '**/api/works/', {
            statusCode: 200,
            body: []
        }).as('getConsumerWorks');

        cy.intercept('GET', `**/api/works/${workId}/`, {
            statusCode: 200,
            body: music
        }).as('getWorkDetails');
    });

    describe('Acceso sin suscripción', () => {
        beforeEach(() => {
            cy.intercept('GET', '**/api/subscriptions/me/', {
                statusCode: 404,
                body: { detail: 'No tienes suscripción activa.' }
            }).as('getMySubscription');

            cy.intercept('GET', '**/api/subscriptions/works/subscribe/', {
                statusCode: 200,
                body: []
            }).as('getSavedWorks');

            cy.loginAsConsumer()
            cy.visit(`/works/${workId}`, {
                onBeforeLoad(win) {
                    win.localStorage.setItem('token', token);
                }
            });

            cy.wait(['@getUserMe', '@getWorkDetails', '@getMySubscription']);
        });

        it('muestra el botón para suscribirse y permite ver la muestra', () => {
            cy.contains('h1.work-main-title', 'Ecos del Atardecer').should('be.visible');
            cy.contains('.circle-pink', 'MÚSICA').should('be.visible');

            cy.get('.locked-zone').should('be.visible');
            cy.contains('.btn-subscribe-now', 'Suscribirse para acceder').should('be.visible');

            cy.get('.btn-download').should('not.exist');

            cy.get('.btn-sidebar-secondary')
                .should('be.visible')
                .and('contain', 'Abrir preview (muestra_ecos_del_atardecer.mp3)');
        });

        it('redirige a /subscription/plans al hacer clic en suscribirse', () => {
            cy.get('.btn-subscribe-now').click();
            cy.url().should('include', '/subscription/plans');
        });

        it('permite guardar y quitar la obra de favoritos', () => {
            cy.intercept('POST', '**/api/subscriptions/works/subscribe/', {
                statusCode: 201,
                body: { work_id: workId }
            }).as('saveWorkReq');

            cy.get('.btn-save-detail').should('not.have.class', 'is-saved');
            cy.get('.btn-save-detail').click();

            cy.wait('@saveWorkReq');
            cy.get('.popup-notification.success')
                .should('be.visible')
                .and('contain', '¡Obra guardada en favoritos!');
            cy.get('.btn-save-detail').should('have.class', 'is-saved').and('contain', 'Guardada');

            cy.intercept('DELETE', '**/api/subscriptions/works/subscribe/', {
                statusCode: 204,
                body: {}
            }).as('deleteSavedReq');

            cy.get('.btn-save-detail').click();
            cy.wait('@deleteSavedReq');
            cy.get('.popup-notification.success')
                .should('be.visible')
                .and('contain', '¡Obra eliminada de tus favoritos!');
            cy.get('.btn-save-detail').should('not.have.class', 'is-saved').and('contain', 'Guardar obra');
        });
    });

    describe('Acceso con suscripción activa', () => {
        beforeEach(() => {
            cy.intercept('GET', '**/api/subscriptions/me/', {
                statusCode: 200,
                body: {
                    plan: { id: 2, name: 'Plan Creador', points: 50 },
                    plan_name: 'Plan Creador',
                    plan_points: 50
                }
            }).as('getMySubscription');

            cy.intercept('GET', '**/api/subscriptions/works/subscribe/', {
                statusCode: 200,
                body: []
            }).as('getSavedWorks');

            cy.loginAsConsumer()
            cy.visit(`/works/${workId}`, {
                onBeforeLoad(win) {
                    win.localStorage.setItem('token', token);
                }
            });

            cy.wait(['@getUserMe', '@getWorkDetails', '@getMySubscription']);
        });

        it('muestra el archivo desbloqueado y permite la descarga del original', () => {
            cy.get('.unlocked-zone').should('be.visible');
            cy.contains('.file-real-name-tag', 'ecos_del_atardecer.mp3').should('be.visible');

            cy.intercept('GET', `**/api/works/${workId}/serve/`, {
                statusCode: 200,
                headers: {
                    'content-disposition': 'attachment; filename="ecos_del_atardecer.mp3"',
                    'content-type': 'audio/mp3'
                },
                body: 'Contenido de la obra completa'
            }).as('serveOriginal');

            cy.get('.btn-download').contains('Descargar Original').click();
            cy.wait('@serveOriginal').its('response.statusCode').should('eq', 200);
        });
    });

    describe('perfil del Autor', () => {
        beforeEach(() => {
            cy.intercept('GET', '**/api/subscriptions/me/', {
                statusCode: 404,
                body: {}
            }).as('getMySubscription');

            cy.intercept('GET', '**/api/subscriptions/works/subscribe/', {
                statusCode: 200,
                body: []
            }).as('getSavedWorks');

            cy.intercept('GET', `**/api/users/${authorId}/`, {
                statusCode: 200,
                body: authorDetails
            }).as('getAuthorProfile');

            cy.intercept('GET', `**/api/works/authors/${authorId}/`, {
                statusCode: 200,
                body: authorWorks
            }).as('getAuthorWorks');

            cy.intercept('GET', `**/api/subscriptions/authors/stats/?author_id=${authorId}`, {
                statusCode: 200,
                body: authorStats
            }).as('getAuthorModalStats');

            cy.loginAsConsumer()
            cy.visit(`/works/${workId}`, {
                onBeforeLoad(win) {
                    win.localStorage.setItem('token', token);
                }
            });

            cy.wait(['@getUserMe', '@getWorkDetails']);
        });

        it('abre el modal del autor, muestra sus estadísticas y lista sus obras', () => {
            cy.get('.btn-author-profile').click();

            cy.wait(['@getAuthorProfile', '@getAuthorWorks', '@getAuthorModalStats']);

            cy.get('.modal-overlay').should('be.visible');
            cy.get('.modal-card').within(() => {
                cy.contains('h2', 'Elena Vázquez').should('be.visible');
                cy.contains('.author-handle', '@elena_art').should('be.visible');

                cy.contains('.stat-number', '2').should('be.visible');
                cy.contains('.stat-number', '14').should('be.visible');
                cy.contains('.stat-number', '89').should('be.visible');

                cy.contains('.section-text', 'Escritora e ilustradora digital con experiencia en narrativa de ficción y diseño conceptual.').should('be.visible');

                cy.get('.modal-works-table tbody tr').should('have.length', 2);
                cy.contains('.work-title-cell', 'El Algoritmo Silencioso').should('be.visible');
            });

            cy.get('.modal-close-btn').click();
            cy.get('.modal-overlay').should('not.exist');
        });

        it('permite suscribirse al autor', () => {
            cy.intercept('POST', '**/api/subscriptions/authors/subscribe/', {
                statusCode: 201,
                body: { author_id: authorId }
            }).as('subToAuthorReq');

            cy.get('.btn-author-profile').click();
            cy.wait('@getAuthorProfile');

            cy.get('.btn-subscribe').contains('Suscribirse a este Autor').click();
            cy.wait('@subToAuthorReq');

            cy.get('.popup-notification.success')
                .should('be.visible')
                .and('contain', '¡Te has suscrito con éxito a este autor!');

            cy.get('.btn-subscribe')
                .contains('Desuscribirse de este Autor')
                .scrollIntoView()
                .should('be.visible')
                .click();
        });
    });
});


describe('Flujo de Catálogo y Directorio de Autores para Consumidor', () => {
    const token = 'consumer-token-catalog-555';

    const mockUser = {
        id: 12,
        username: 'carlos_reader',
        role: 'consumer',
        interests: 'libro,software'
    };

    const works = [
        {
            id: 1,
            title: 'Aprende Vue en 30 Días',
            work_type: 'software',
            plan_required: { id: 1, name: 'Plan Básico' },
            created_at: '2026-06-01T10:00:00Z'
        },
        {
            id: 2,
            title: 'Sinfonía en Re Menor',
            work_type: 'music',
            plan_required: null,
            created_at: '2026-07-15T12:00:00Z'
        },
        {
            id: 3,
            title: 'El Castillo Olvidado',
            work_type: 'book',
            plan_required: { id: 2, name: 'Plan Creador' },
            created_at: '2026-08-01T08:00:00Z'
        }
    ];

    const plans = [
        { id: 1, name: 'Plan Básico', points: 30 },
        { id: 2, name: 'Plan Creador', points: 50 }
    ];

    const authors = [
        {
            id: 21,
            username: 'clara_escritora',
            first_name: 'Clara',
            last_name: 'Martínez',
            biography: 'Escritora de literatura contemporánea.'
        },
        {
            id: 22,
            username: 'dev_alberto',
            first_name: 'Alberto',
            last_name: 'Ruiz',
            biography: 'Desarrollador y creador de contenidos técnicos.'
        }
    ];

    beforeEach(() => {
        cy.intercept('GET', '**/api/users/me/', { statusCode: 200, body: mockUser }).as('getUserMe');
        cy.intercept('GET', '**/api/works/', { statusCode: 200, body: works }).as('getWorks');
        cy.intercept('GET', '**/api/subscriptions/plans/', { statusCode: 200, body: plans }).as('getPlans');
        cy.intercept('GET', '**/api/users/authors/', { statusCode: 200, body: authors }).as('getAuthors');
        cy.intercept('GET', '**/api/subscriptions/works/subscribe/', { statusCode: 200, body: [] }).as('getSavedWorks');
        cy.intercept('GET', '**/api/subscriptions/authors/subscribe/', { statusCode: 200, body: [] }).as('getSubscribedAuthors');
        cy.intercept('GET', '**/api/subscriptions/me/', { statusCode: 200, body: null }).as('getMySubscription');
        cy.intercept('GET', '**/api/subscriptions/points/', { statusCode: 200, body: { points: 80 } }).as('getPoints');

        cy.loginAsConsumer()
        cy.visit('/works', {
            onBeforeLoad(win) {
                win.localStorage.setItem('token', token);
            }
        });

        cy.wait(['@getUserMe', '@getWorks', '@getPlans', '@getAuthors']);
    });

    describe('Pestaña de Obras', () => {
        it('muestra la lista de obras con sugerencia según los intereses del usuario', () => {
            cy.contains('h1', 'Catálogo de Obras Disponibles').should('be.visible');

            cy.get('.catalog-table tbody tr').should('have.length', 3);

            cy.contains('tr', 'Aprende Vue en 30 Días').within(() => {
                cy.contains('.badge-interes', '⭐ Sugerido').should('be.visible');
            });

            cy.contains('tr', 'Sinfonía en Re Menor').within(() => {
                cy.contains('.badge-neutral', '-').should('be.visible');
            });
        });

        it('filtra obras por el campo de texto', () => {
            cy.get('.filter-input').type('Castillo');

            cy.get('.catalog-table tbody tr').should('have.length', 1);
            cy.contains('.work-title', 'El Castillo Olvidado').should('be.visible');
            cy.contains('.work-title', 'Sinfonía').should('not.exist');
        });

        it('permite guardar y retirar una obra de favoritos desde la tabla', () => {
            cy.intercept('POST', '**/api/subscriptions/works/subscribe/', {
                statusCode: 201,
                body: { work_id: 1 }
            }).as('saveWorkReq');

            cy.contains('tr', 'Aprende Vue en 30 Días').within(() => {
                cy.get('button[title="Guardar obra"]').click();
            });

            cy.wait('@saveWorkReq');
            cy.get('.popup-notification.success')
                .should('be.visible')
                .and('contain', '¡Te has guardado con éxito esta obra!');

            cy.contains('tr', 'Aprende Vue en 30 Días').within(() => {
                cy.get('button[title="Quitar de guardados"]').should('exist');
            });
        });
    });

    describe('Pestaña de Directorio de Autores', () => {
        beforeEach(() => {
            cy.contains('.pill-btn', 'Autores').click();
        });

        it('cambia de modo y muestra las tarjetas de autores registrados', () => {
            cy.contains('h1', 'Directorio de Autores').should('be.visible');
            cy.get('.author-card').should('have.length', 2);
            cy.contains('.author-card', 'clara_escritora').should('be.visible');
            cy.contains('.author-card', 'dev_alberto').should('be.visible');
        });

        it('filtra autores por usuario', () => {
            cy.get('input[placeholder*="nombre o usuario"]').type('alberto');

            cy.get('.author-card').should('have.length', 1);
            cy.contains('.author-card', 'dev_alberto').should('be.visible');
            cy.contains('.author-card', 'clara_escritora').should('not.exist');
        });

        it('abre el modal del autor y permite suscribirse', () => {
            cy.intercept('GET', '**/api/works/authors/21/', {
                statusCode: 200,
                body: [{ id: 3, title: 'El Castillo Olvidado', work_type: 'book', status: 'published', created_at: '2026-08-01' }]
            }).as('getAuthorWorks');

            cy.intercept('GET', '**/api/subscriptions/authors/stats/?author_id=21', {
                statusCode: 200,
                body: { subscribers_count: 5, saved_works_count: 12 }
            }).as('getAuthorStats');

            cy.intercept('POST', '**/api/subscriptions/authors/subscribe/', {
                statusCode: 201,
                body: { author_id: 21 }
            }).as('subAuthorReq');

            cy.contains('.author-card', 'clara_escritora').within(() => {
                cy.contains('button', 'Ver Perfil').click();
            });

            cy.wait(['@getAuthorWorks', '@getAuthorStats']);

            cy.get('.modal-overlay').should('be.visible');
            cy.contains('.modal-card h2', 'Clara Martínez').should('be.visible');
            cy.contains('.stat-data', '5').should('be.visible');

            cy.contains('button.btn-subscribe', 'Suscribirse a este Autor')
                .click({ force: true });
            cy.wait('@subAuthorReq');

            cy.get('.popup-notification.success')
                .should('be.visible')
                .and('contain', '¡Te has suscrito con éxito a este autor!');
            cy.get('.btn-subscribe').should('contain', 'Desuscribirse de este Autor');

            cy.get('.modal-close-btn').click();
            cy.get('.modal-overlay').should('not.exist');
        });
    });
});