describe('Flujo de Obras Favoritas', () => {
    const token = 'consumer-token-catalog-555';

    const user = {
        id: 15,
        username: 'carlos_reader',
        email: 'carlos@example.com',
        role: 'consumer'
    };

    const subscription = {
        plan_name: 'Plan Creador',
        end_date: '2026-12-31T23:59:59Z'
    };

    const savedWorks = [
        {
            id: 1,
            work_id: 101,
            title: 'El enigma de las sombras',
            work_type: 'book',
            author_username: 'elena_art'
        },
        {
            id: 2,
            work_id: 102,
            title: 'Ecos del Atardecer',
            work_type: 'music',
            author_username: 'lucia_beats'
        },
        {
            id: 3,
            work_id: 103,
            title: 'Microservicio de Autenticación Criptográfica',
            work_type: 'software',
            author_username: 'lucas_lopez'
        }
    ];

    beforeEach(() => {
        cy.intercept('GET', '**/api/users/me/', {
            statusCode: 200,
            body: user
        }).as('getUserMe');

        cy.intercept('GET', '**/api/subscriptions/points/', {
            statusCode: 200,
            body: { points: 120 }
        }).as('getUserPoints');

        cy.intercept('GET', '**/api/subscriptions/me/', {
            statusCode: 200,
            body: subscription
        }).as('getMySubscription');

        cy.intercept('GET', '**/api/users/notifications/', {
            statusCode: 200,
            body: []
        }).as('getNotifications');

        cy.intercept('GET', '**/api/subscriptions/works/subscribe/', {
            statusCode: 200,
            body: savedWorks
        }).as('getSavedWorks');

        cy.intercept('GET', '**/api/works/**', { statusCode: 200, body: [] });

        cy.loginAsConsumer()
        cy.visit('/subscription/works/subscribe', {
            onBeforeLoad(win) {
                win.localStorage.setItem('token', token);
            }
        });

        cy.wait(['@getUserMe', '@getUserPoints', '@getSavedWorks', '@getMySubscription']);
    });

    it('mostrar la cabecera, los badges del consumidor y la lista de obras favoritas', () => {
        cy.contains('.nav-user', 'carlos_reader').should('be.visible');
        cy.contains('.consumer-badges .points', 'Plan Creador').should('be.visible');
        cy.contains('.consumer-badges .points', '120 Puntos').should('be.visible');

        cy.contains('h1', 'Mis obras favoritas').should('be.visible');

        cy.get('.work-custom-card').should('have.length', 3);

        cy.contains('.work-custom-card', 'El enigma de las sombras').within(() => {
            cy.contains('.work-card-author', 'Autor @elena_art').should('be.visible');
            cy.contains('.pill-type-tag', 'Libro').should('be.visible');
            cy.get('.btn-bookmark-action i.fa-bookmark').should('have.class', 'fa-solid');
            cy.contains('.btn-card-details', 'Ver detalles').should('be.visible');
        });

        cy.contains('.work-custom-card', 'Ecos del Atardecer').within(() => {
            cy.contains('.pill-type-tag', 'Música').should('be.visible');
        });
        cy.contains('.work-custom-card', 'Microservicio de Autenticación Criptográfica').within(() => {
            cy.contains('.pill-type-tag', 'Software').should('be.visible');
        });
    });

    it('filtra las obras guardadas', () => {
        cy.get('.filter-input').type('Ecos del Atardecer');

        cy.get('.work-custom-card').should('have.length', 1);
        cy.contains('.work-card-title', 'Ecos del Atardecer').should('be.visible');
        cy.contains('.work-card-title', 'El enigma de las sombras').should('not.exist');

        cy.get('.filter-input').clear().type('Texto');
        cy.get('.work-custom-card').should('not.exist');
        cy.contains('.empty-msg', 'No se han encontrado obras que coincidan con la búsqueda.').should('be.visible');
    });

    it('elimina la obra de favoritos', () => {
        cy.intercept('DELETE', '**/api/subscriptions/works/subscribe/', {
            statusCode: 204,
            body: {}
        }).as('deleteSavedWorkReq');

        cy.contains('.work-custom-card', 'El enigma de las sombras').within(() => {
            cy.get('.btn-bookmark-action').click();
        });

        cy.get('.btn-confirm').click();

        cy.wait('@deleteSavedWorkReq').its('response.statusCode').should('eq', 204);

        cy.get('.popup-notification.success')
            .should('be.visible')
            .and('contain', '¡Obra eliminada de tus favoritos!');

        cy.get('.work-custom-card').should('have.length', 2);
        cy.contains('.work-custom-card', 'El Laberinto de Papel').should('not.exist');
    });

    it('el enlace "Ver detalles" redirige a la vista de detalle de la obra', () => {
        cy.contains('.work-custom-card', 'El enigma de las sombras').within(() => {
            cy.contains('.btn-card-details', 'Ver detalles').should('have.attr', 'href', '/works/101');
        });
    });

    it('el botón "Volver" regresa al Dashboard sin provocar logout', () => {
        cy.get('.btn-back-top').click();
        cy.url({ timeout: 6000 }).should('include', '/dashboard');
    });
});

describe('Flujo de Autores Seguidos', () => {
    const token = 'consumer-token-catalog-555';

    const user = {
        id: 15,
        username: 'carlos_reader',
        email: 'carlos@example.com',
        role: 'consumer'
    };

    const subscription = {
        plan_name: 'Plan Creador',
        end_date: '2026-12-31T23:59:59Z'
    };

    const subscribedAuthors = [
        {
            id: 21,
            username: 'elena_art',
            first_name: 'Elena',
            last_name: 'Vázquez',
            biography: 'Escritora e ilustradora digital con experiencia en narrativa de ficción y diseño conceptual.'
        },
        {
            id: 22,
            username: 'lucia_beats',
            first_name: 'Lucía',
            last_name: 'Navarro',
            biography: 'Desarrolladora de música'
        }
    ];

    const authorWorks = [
        {
            id: 101,
            title: 'El enigma de las sombras',
            work_type: 'book',
            status: 'published',
            created_at: '2026-12-31T23:59:59Z'
        }
    ];

    const authorStats = {
        subscribers_count: 5,
        saved_works_count: 12
    };

    beforeEach(() => {
        cy.intercept('GET', '**/api/users/me/', {
            statusCode: 200,
            body: user
        }).as('getUserMe');

        cy.intercept('GET', '**/api/subscriptions/points/', {
            statusCode: 200,
            body: { points: 150 }
        }).as('getUserPoints');

        cy.intercept('GET', '**/api/subscriptions/me/', {
            statusCode: 200,
            body: subscription
        }).as('getMySubscription');

        cy.intercept('GET', '**/api/users/notifications/', {
            statusCode: 200,
            body: []
        }).as('getNotifications');

        cy.intercept('GET', '**/api/subscriptions/authors/subscribe/', {
            statusCode: 200,
            body: subscribedAuthors
        }).as('getSubscribedAuthors');

        cy.intercept('GET', '**/api/works/**', { statusCode: 200, body: [] });

        cy.loginAsConsumer()
        cy.visit('/subscription/authors/subscribe', {
            onBeforeLoad(win) {
                win.localStorage.setItem('token', token);
            }
        });

        cy.wait(['@getUserMe', '@getUserPoints', '@getSubscribedAuthors', '@getMySubscription']);
    });

    it('renderiza la lista de autores seguidos con sus tarjetas y datos', () => {
        cy.contains('h1', 'Mis autores').should('be.visible');
        cy.contains('.nav-user', 'carlos_reader').should('be.visible');
        cy.contains('.consumer-badges .points', 'Plan Creador').should('be.visible');

        cy.get('.author-card').should('have.length', 2);

        cy.contains('.author-card', 'elena_art').within(() => {
            cy.contains('h3', 'elena_art').should('be.visible');
            cy.contains('.author-badge', 'Autor Registrado').should('be.visible');
            cy.contains('.author-bio', 'Escritora e ilustradora digital con experiencia en narrativa de ficción y diseño conceptual.').should('be.visible');
            cy.contains('button.btn-table', 'Ver Perfil').should('be.visible');
        });

        cy.contains('.author-card', 'lucia_beats').should('be.visible');
    });

    it('filtra los autores', () => {
        cy.get('.filter-input').type('Lucia');

        cy.get('.author-card').should('have.length', 1);
        cy.contains('.author-card', 'lucia_beats').should('be.visible');
        cy.contains('.author-card', 'elena_art').should('not.exist');

        cy.get('.filter-input').clear().type('Carlos');
        cy.get('.author-card').should('not.exist');
        cy.contains('.empty-msg', 'No se han encontrado autores que coincidan con la búsqueda.').should('be.visible');
    });

    it('abre el modal del autor y muestra sus estadísticas', () => {
        cy.intercept('GET', '**/api/works/authors/21/', {
            statusCode: 200,
            body: authorWorks
        }).as('getAuthorWorks');

        cy.intercept('GET', '**/api/subscriptions/authors/stats/?author_id=21', {
            statusCode: 200,
            body: authorStats
        }).as('getAuthorStats');

        cy.contains('.author-card', 'elena_art').within(() => {
            cy.contains('button', 'Ver Perfil').click();
        });

        cy.wait(['@getAuthorWorks', '@getAuthorStats']);

        cy.get('.modal-overlay').should('be.visible');
        cy.get('.modal-card').within(() => {
            cy.contains('h2', 'Elena Vázquez').should('be.visible');
            cy.contains('.author-handle', '@elena_art').should('be.visible');

            cy.contains('.stat-label', 'Suscriptores').parent().contains('.stat-number', '5');
            cy.contains('.stat-label', 'Obras publicadas').parent().contains('.stat-number', '1');

            cy.get('.modal-works-table tbody tr').should('have.length', 1);
            cy.contains('.work-title-cell', 'El enigma de las sombras').should('be.visible');
        });

        cy.get('.modal-close-btn').click();
        cy.get('.modal-overlay').should('not.exist');
    });

    it('cancela la suscripción al autor', () => {
        cy.intercept('GET', '**/api/works/authors/21/', {
            statusCode: 200,
            body: authorWorks
        }).as('getAuthorWorks');

        cy.intercept('GET', '**/api/subscriptions/authors/stats/?author_id=21', {
            statusCode: 200,
            body: authorStats
        }).as('getAuthorStats');

        cy.intercept('DELETE', '**/api/subscriptions/authors/subscribe/', {
            statusCode: 204,
            body: {}
        }).as('cancelSubscriptionReq');

        cy.contains('.author-card', 'elena_art').within(() => {
            cy.contains('button', 'Ver Perfil').click();
        });
        cy.wait(['@getAuthorWorks', '@getAuthorStats']);

        cy.contains('button.btn-subscribe', 'Anular suscripción a este Autor')
            .click({ force: true });

        cy.get('.popup-notification')
            .should('be.visible')
            .and('contain', 'Confirmar Acción')
            .and('contain', '¿Estás seguro de que deseas dejar de seguir a este autor?');

        cy.get('.btn-confirm').click();

        cy.wait('@cancelSubscriptionReq').its('response.statusCode').should('eq', 204);

        cy.get('.popup-notification.success')
            .should('be.visible')
            .and('contain', '¡Has cancelado tu suscripción a este autor!');

        cy.get('.modal-overlay').should('not.exist');
        cy.get('.author-card').should('have.length', 1);
        cy.contains('.author-card', 'clara_escritora').should('not.exist');
    });

    it('el botón "Volver" regresa al Dashboard correctamente', () => {
        cy.intercept('GET', '**/api/subscriptions/**', { statusCode: 200, body: [] });

        cy.get('.btn-back-top').click();
        cy.url({ timeout: 6000 }).should('include', '/dashboard');
    });
});

describe('Flujo de Planes de Suscripción', () => {
    const token = 'consumer-token-plans-321';
  
    const user = {
        id: 15,
        username: 'carlos_reader',
        email: 'carlos@example.com',
        role: 'consumer'
    };
  
    const plans = [
      {
        id: 1,
        name: 'Plan Básico',
        points: 30,
        price: '2.99',
        description: 'Descarga de muestras/resúmenes .',
        duration_days: 30
      },
      {
        id: 2,
        name: 'Plan Creador',
        points: 50,
        price: '4.99',
        description: 'Acceso al catálogo digital estándar, audios completos y resolución HD.',
        duration_days: 30
      },
      {
        id: 3,
        name: 'Plan Mecenas',
        points: 300,
        price: '29.99',
        description: 'Acceso a obras exclusivas, descargas de código/ficheros originales y contacto directo.',
        duration_days: 365
      }
    ];
  
    const userSubscription = {
      plan: { id: 1, name: 'Plan Creador' },
      plan_name: 'Plan Creador',
      end_date: '2026-12-31T23:59:59Z'
    };
  
    beforeEach(() => {
      cy.intercept('GET', '**/api/users/me/', {
        statusCode: 200,
        body: user
      }).as('getUserMe');
  
      cy.intercept('GET', '**/api/subscriptions/points/', {
        statusCode: 200,
        body: { points: 120 }
      }).as('getUserPoints');
  
      cy.intercept('GET', '**/api/subscriptions/plans/', {
        statusCode: 200,
        body: plans
      }).as('getPlans');
  
      cy.intercept('GET', '**/api/subscriptions/me/', {
        statusCode: 200,
        body: userSubscription
      }).as('getMySubscription');
  
      cy.intercept('GET', '**/api/works/**', { statusCode: 200, body: [] });
  
      cy.loginAsConsumer()
      cy.visit('/subscription/plans', {
        onBeforeLoad(win) {
          win.localStorage.setItem('token', token);
        }
      });
  
      cy.wait(['@getPlans', '@getUserMe', '@getMySubscription', '@getUserPoints']);
    });
  
    it('muestra la lista de planes', () => {
      cy.contains('h1.title-welcome', 'Encuentra el plan perfecto para ti').should('be.visible');
  
      cy.get('.plan-card').should('have.length', 3);
  
      cy.contains('.plan-card', 'Plan Básico').within(() => {
        cy.contains('.plan-price', '30 puntos').should('be.visible');
        cy.contains('.money-equivalence', 'Equivale a 2.99 € / mes').should('be.visible');
        cy.contains('.number-highlight', '30 días').should('be.visible');
  
        cy.get('button.btn-plan-actual')
          .should('be.disabled')
          .and('contain', 'Plan actual');
      });
  
      cy.contains('.plan-card', 'Plan Creador').within(() => {
        cy.contains('.plan-price', '50 puntos').should('be.visible');
        cy.contains('.money-equivalence', 'Equivale a 4.99 € / mes').should('be.visible');
  
        cy.contains('button.btn-accion', 'Seleccionar Plan Creador')
          .should('not.be.disabled')
          .and('be.visible');
      });
    });
  
    it('cancela la suscripción', () => {
      cy.contains('.plan-card', 'Plan Creador').within(() => {
        cy.contains('button.btn-accion', 'Seleccionar Plan Creador').click();
      });
  
      cy.get('.popup-notification')
        .should('be.visible')
        .and('contain', '¿Estás seguro de que deseas suscribirte a este plan?');
  
       
      cy.get('.btn-cancel').click();
      cy.get('.popup-notification').should('not.exist');
    });
  
    it('contrata exitosamente un nuevo plan', () => {
      cy.intercept('POST', '**/api/subscriptions/subscribe/', {
        statusCode: 200,
        body: { detail: '¡Suscripción realizada con éxito!' }
      }).as('subscribeRequest');
  
      cy.contains('.plan-card', 'Plan Mecenas').within(() => {
        cy.contains('button.btn-accion', 'Seleccionar Plan Mecenas').click();
      });
  
      cy.get('.popup-notification').should('be.visible');
      cy.get('.btn-confirm').click();
  
      cy.wait('@subscribeRequest').then((interception) => {
        expect(interception.request.body).to.deep.equal({ plan_id: 3 });
        expect(interception.response.statusCode).to.eq(200);
      });
  
      cy.get('.popup-notification.success')
        .should('be.visible')
        .and('contain', '¡Suscripción realizada con éxito!');
    });
  
    it('muestra un mensaje de error si el backend deniega la suscripción', () => {
      cy.intercept('POST', '**/api/subscriptions/subscribe/', {
        statusCode: 400,
        body: { detail: 'No tienes puntos suficientes en tu saldo para contratar este plan.' }
      }).as('subscribeFailed');
  
      cy.contains('.plan-card', 'Plan Mecenas').within(() => {
        cy.contains('button.btn-accion', 'Seleccionar Plan Mecenas').click();
      });
  
      cy.get('.btn-confirm').click();
  
      cy.wait('@subscribeFailed');
  
      cy.get('.popup-notification.error')
        .should('be.visible')
        .and('contain', 'No tienes puntos suficientes en tu saldo');
    });
  
    it('el botón "Volver" navega al Dashboard', () => {
      cy.intercept('GET', '**/api/subscriptions/**', { statusCode: 200, body: [] });
  
      cy.get('.btn-back-top').click();
      cy.url({ timeout: 6000 }).should('include', '/dashboard');
    });
  });