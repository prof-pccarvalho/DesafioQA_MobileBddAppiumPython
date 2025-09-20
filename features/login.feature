Feature: Login no app Sauce Labs

  Scenario: Login com sucesso
    Given que o app está aberto na tela de login
    When eu digito o usuário "visual@example.com" e a senha "10203040"
    And clico no botão de login
    Then devo ver a tela inicial do app