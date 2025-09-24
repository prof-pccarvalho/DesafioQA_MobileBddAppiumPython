Feature: Comparar produtos no catálogo

  Background:
    Given que o app está aberto na tela de login
    Given que estou logado como "visual@example.com" e senha "10203040"
    # Opcional: pode validar a tela inicial se desejar
    Then devo ver a tela inicial do app

  Scenario: Comparar dois produtos distintos no catálogo
    When eu comparo os produtos 1 e 2
    Then os títulos dos produtos devem ser diferentes

  Scenario: Comparar dois produtos iguais (exemplo)
    When eu comparo os produtos 1 e 1
    Then os títulos dos produtos devem ser iguais
