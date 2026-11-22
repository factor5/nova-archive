Feature: Installable app, offline use and updates
  As a phone user
  I want the app to install and work offline
  And pick up new versions without stale files

  Background:
    Given a fresh browser profile
    And the app has been opened once online

  @PW-01 @smoke @sw
  Scenario: A service worker is registered
    Then a service worker for the app scope is active

  @PW-02 @sw
  Scenario: The shell is precached
    Then the cache "nova-v<VERSION>" contains every file in the SHELL list
    And the VERSION matches the app version shown on the About page

  @PW-03 @smoke @sw
  Scenario: The app works offline
    When the network goes offline and I reload
    Then the Library loads with 1329 books
    And I can mark a book read and the change persists

  @PW-04 @sw
  Scenario: Pages not yet visited work offline too
    When I go offline and open the book page for "Dune"
    Then it renders from local data

  @PW-05 @sw @wip
  Scenario: Online, fresh files are preferred
    Given the server now serves a changed "css/base.css"
    When I reload online
    Then the changed file is used

  @PW-06 @sw
  Scenario: Version query strings do not break offline fallback
    When offline, "js/main.js?v=999" is requested
    Then the cached "js/main.js" is returned

  @PW-07 @sw
  Scenario: Old caches are removed on update
    Given a cache "nova-v1" exists
    When the new service worker activates
    Then "nova-v1" is deleted

  @PW-08 @sw @wip
  Scenario: Third-party assets use stale-while-revalidate
    Then the Firebase SDK and font requests are answered from cache when present and refreshed in the background

  @PW-09 @sw
  Scenario: Open Library and Firestore calls are never cached by the worker
    Then requests to openlibrary.org and firestore.googleapis.com bypass the cache

  @PW-10
  Scenario: Manifest is installable
    Then the manifest has name "Nova Archive — Sci-Fi Award Library", display "standalone", start_url inside scope
    And icons of 192 and 512 px and a maskable icon exist and load

  @PW-11
  Scenario: Version consistency
    Then the service worker VERSION, the "?v=" in index.html, the app-version meta and the SHELL list all agree
    # automated by: python3 tests/support/check_repo.py (see 12-data-integrity)

  @PW-12 @manual
  Scenario: Install on Android
    When I open the site in Chrome on Android
    Then "Install app" is offered
    And the installed app opens full screen with the right icon and theme colour
