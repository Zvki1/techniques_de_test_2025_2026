# Plan de Tests - Triangulator

## Vue d'ensemble

Dans ce projet on va essayer de suivre l'approce Test-Driven Development ou les test sont ecrits avant l'implémentation

---

## 1. Tests Unitaires

### 1.1 Tests de Format Binaire - PointSet

**Objectif** : Valider l'encodage et le décodage du format binaire PointSet

**Tests d'encodage** :
- Ensemble vide (0 points)
- 1 point
- N points (3, 10, 100)
- Valeurs négatives
- Valeurs limites (float min/max)

**Tests de décodage** :
- Format valide
- Format corrompu (nombre de bytes incorrect)
- Données incohérentes (N déclaré ≠ N réel)


### 1.2 Tests de Format Binaire - Triangles

**Objectif** : Valider l'encodage et le décodage du format binaire Triangles

**Tests d'encodage** :
- 0 triangle
- 1 triangle (3 vertices)
- N triangles
- Indices hors limite (détection d'erreur)

**Tests de décodage** :
- Format valide (partie poinset + partie triangles)
- Partie pointSet invalide
- Partie triangles invalide
- Nombre de triangles incohérent


### 1.3 Tests de l'Algorithme de Triangulation

**Objectif** : Valider le comportement de l'algorithme de triangulation

**Cas normaux** :
- 3 points (triangle minimal) → 1 triangle
- 4 points (carré) → 2 triangles
- N points combien de triangles ??

**Cas limites** :
- < 3 points → Exception
- Points alignés sur le meme x ou y → Exception ou gestion spécifique
- Points en double → Dédoublonnage ou erreur

**Propriétés géométriques** :
- Tous les sommets sont utilisés dans au moins un triangle
- Pas de triangles qui se chevauchent

---

## 2. Tests d'Intégration

### 2.1 Communication avec PointSetManager

**Objectif** : Valider l'interaction avec le PointSetManager

**Utilisation de Mocks/Stubs** :
- Simuler les réponses du PointSetManager 

**Scénarios testés** :
- Requête réussie (200 + PointSet binaire valide)
- PointSet inexistant (404)
- Erreur serveur PointSetManager (500)
- Format de réponse invalide (données corrompues)

**Validation** :
- Le Triangulator gère correctement chaque cas
- Les codes d'erreur HTTP appropriés sont retournés (404, 500, 503)

---

## 3. Tests Système (Conformité API)

### 3.1 Tests de conformité OpenAPI

**Objectif** : Vérifier que l'API respecte la spécification `triangulator.yml`

### 3.2 Endpoint GET /triangulation/{pointSetId}

**Cas de succès (200)** :
- UUID valide + PointSet existant → Triangles en binaire
- Content-Type: `application/octet-stream`
- Format binaire Triangles correct

**Cas d'erreur (4xx)** :
- UUID invalide → 400 + JSON error
- UUID inexistant → 404 + JSON error

**Cas d'erreur (5xx)** :
- Triangulation échoue → 500 + JSON error
- PointSetManager inaccessible → 503 + JSON error

**Validation des erreurs** :
- Format JSON conforme : `{"code": "...", "message": "..."}`
- Content-Type: `application/json`
- Messages d'erreur explicites

**Tests additionnels** :
- Méthode non autorisée (POST, PUT, DELETE) → 405
- Route invalide → 404

---

## 4. Tests de Performance

**Objectif** : Mesurer les performances et identifier les limites du système

### 4.1 Tests de montée en charge

**Différents nombres de sommets** :
- 10 points → temps de triangulation
- 100 points → temps de triangulation
- 1000 points → temps de triangulation
- 10000 points → temps de triangulation 

**Métriques mesurées** :
- Temps d'exécution de la triangulation
- Temps d'encodage/décodage des formats binaires

## 5. Tests de Couverture

**Objectif** : S'assurer que tout le code est testé