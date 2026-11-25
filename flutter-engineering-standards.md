# Flutter Engineering Standards

A practical guide to writing Flutter apps that are clean, fast, safe and easy to change, for everyone on the team, from product owners to senior engineers.

Version 1.1 · November 2026 · Applies to any Flutter app. State, dependency injection and navigation examples cover GetX, Provider, Riverpod and Bloc; networking examples use Dio.

---

## How to use this guide

**Audience:** Everyone

You don't have to read everything. Pick your path:

| You are | Read these sections | Time |
|---|---|---|
| Non-technical (product owner, manager, QA, client) | 1, 2, Glossary | 15 min |
| Beginner (new to Flutter) | 1 to 4, 6, 11, Glossary | 45 min |
| Junior developer | Everything | 2 hours |
| Senior developer or tech lead | Everything. You enforce it in code review. | 2 to 3 hours |

Each section starts with an **Audience** line and, where useful, an **In plain words** box that explains the idea without code.

The rules work with any state-management approach. Where code differs, sections 6, 7 and 8 show the same example for **GetX**, **Provider**, **Riverpod** and **Bloc**. In the HTML version, pick your approach once and every example switches to it.

The rule words mean:

- **MUST**: required. A pull request that breaks it should not be merged.
- **SHOULD**: the default. Break it only with a written reason.
- **AVOID**: allowed in rare cases, but a reviewer will ask why.

---

## 1. The ten golden rules

**Audience:** Everyone

If you remember nothing else, remember these.

1. **One job per piece of code.** A screen draws, a controller decides, a repository fetches. Don't mix them.
2. **Zero analyzer warnings.** `flutter analyze` must say "No issues found!" before every merge.
3. **No secrets in the app.** API secrets, encryption keys and passwords never go in source code or on the phone.
4. **Pass dependencies in; don't reach out for them.** Classes receive what they need through their constructor.
5. **Small files, small widgets.** If a file passes about 400 lines, split it.
6. **Never hard-code text, colors or sizes in widgets.** Use translations, the theme and shared constants.
7. **Clean up what you start.** Every timer, stream, controller and focus node is disposed.
8. **Handle every error on purpose.** No empty `catch`, no `print` left behind, and a clear message for the user.
9. **Test the flows that make money.** Search, book, pay and log in each need an automated test that passes in CI.
10. **Delete, don't comment out.** Git remembers old code, so the file doesn't need to.

---

## 2. Quality in plain words

**Audience:** Everyone (written for non-technical readers)

> **In plain words:** Think of the app as a bus company. The **screen** is the ticket counter: it talks to customers and nothing else. The **controller** is the clerk who decides what to do with a request. The **repository** is the back office that fetches records. The **API** is head office. When the counter clerk starts driving buses, everything gets slow and confusing. Good code keeps everyone in their own job.

| Word | What it means | Why the business cares |
|---|---|---|
| Clean code | Code another developer can read and change safely | New features ship faster, with fewer bugs |
| Code standard | Shared rules for naming, layout and structure | Any developer can work on any part of the app |
| Reusable | Build a part once, use it in many places | Less work, and the app looks and behaves the same everywhere |
| Design pattern | A proven way to organise code for a common problem | Fewer surprises, and easier onboarding |
| Performance | The app opens fast, scrolls smoothly and saves battery | Users stay; app store ratings go up |
| Technical debt | Shortcuts that make later changes slower | Ignored debt turns a 1-day change into a 1-week change |
| Test | Code that automatically checks other code | Bugs are caught before customers see them |

---

## 3. Project structure

**Audience:** Beginner, Junior, Senior

> **In plain words:** Files are grouped by *feature* (bus search, booking, profile), like departments in a building, instead of by *type*. Everything about booking lives in the booking folder.

Use a **feature-first** layout:

```text
lib/
├── main.dart                 # Starts the app. Nothing else.
└── app/
    ├── app.dart              # MaterialApp / GetMaterialApp setup
    ├── config/               # Environment values (base URL, timeouts)
    ├── core/                 # Shared by every feature
    │   ├── network/          # Dio client, interceptors, API errors
    │   ├── storage/          # Secure storage, preferences
    │   ├── widgets/          # Reusable UI: buttons, fields, dialogs
    │   ├── theme/            # Colors, text styles, spacing
    │   └── utils/            # Small pure helpers (formatting, validation)
    ├── routes/               # Route names and page registration
    ├── lang/                 # Translations and localization: text, dates, currency
    └── features/             # Or "modules/". One folder per feature.
        └── booking/
            ├── bindings/     # Registers dependencies (GetX bindings or providers)
            ├── state/        # Controllers, notifiers, cubits or blocs
            ├── data/         # Repositories, API services, DTOs
            ├── models/       # Domain models
            ├── screens/      # Full pages
            └── widgets/      # Pieces used only by this feature
```

Rules:

- **MUST** put code used by two or more features in `core/`, and code used by one feature inside that feature.
- **MUST** spell folder names correctly and consistently (`utils`, not `utlis`; `register_binding.dart`, not `register_bindig.dart`). Typos spread through imports and searches.
- **MUST NOT** import one feature's internal files from another feature. Share through `core/` or a public model.
- **SHOULD** keep `main.dart` short: initialise services, then call `runApp`.
- **SHOULD** keep large static data (city lists, NRC codes) as JSON in `assets/` and load it when needed, not as a giant Dart file.
- **AVOID** names like `demo_` or `temp_` in code that will ship. Put prototypes behind an interface (see section 5) and name the real thing properly.

---

## 4. Naming, formatting and lint

**Audience:** Beginner, Junior, Senior

| Thing | Style | Example |
|---|---|---|
| Files and folders | `snake_case` | `seat_plan_screen.dart` |
| Classes, enums, typedefs | `PascalCase` | `SeatPlanController` |
| Variables, functions, parameters | `camelCase` | `selectedSeats`, `loadTrips()` |
| Constants | `camelCase` (Dart style) | `const apiTimeout = Duration(seconds: 20);` |
| Private members | leading `_` | `_refreshToken()` |
| Booleans | read as a question | `isLoading`, `hasAcceptedTerms`, `canBook` |
| Screens / controllers / repositories | suffix by role | `LoginScreen`, `LoginController`, `AuthRepository` |

Formatting:

- **MUST** run `dart format .` before committing. Never argue about spacing in review; the formatter decides.
- **MUST** use package imports (`package:my_app/...`) or relative imports consistently across the whole project. Pick one.

Lint: the default `flutter_lints` set is a minimum. Start new projects with this `analysis_options.yaml`:

```yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  language:
    strict-casts: true
    strict-raw-types: true
  errors:
    unused_import: error
    dead_code: error
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"
    - build/**

linter:
  rules:
    - always_declare_return_types
    - avoid_print
    - avoid_dynamic_calls
    - avoid_empty_else
    - cancel_subscriptions
    - close_sinks
    - prefer_const_constructors
    - prefer_const_declarations
    - prefer_final_fields
    - prefer_final_locals
    - prefer_single_quotes
    - require_trailing_commas
    - unawaited_futures
    - use_build_context_synchronously
    - use_super_parameters
```

Comments:

- **SHOULD** explain *why*, not *what*. The code already says what.
- **MUST NOT** leave commented-out code, `print`, or `debugPrint("here")` in merged code.
- **SHOULD** write a `///` doc comment on every public class and on any method whose behaviour is not obvious.

---

## 5. Architecture: layers and design patterns

**Audience:** Junior, Senior

> **In plain words:** The app is built in layers, like floors in a building. Each floor only talks to the floor directly below it. If head office (the server) changes, only the bottom floor needs to change.

```text
┌──────────────────────────────────────────────┐
│  UI layer        Screens and widgets          │  draws state, sends user actions
├──────────────────────────────────────────────┤
│  State layer     Controllers                  │  holds screen state, decides
├──────────────────────────────────────────────┤
│  Data layer      Repositories (interfaces)    │  one place per data source
│                  API services, storage        │  Dio / Retrofit, secure storage
└──────────────────────────────────────────────┘
        Dependencies point DOWN only. Never up.
```

| Layer | Does | Never does |
|---|---|---|
| Screen / widget | Builds UI from state; forwards taps to the controller | Calls the API, parses JSON, holds business rules |
| Controller (or notifier, cubit, bloc) | Holds state; validates input; calls repositories; maps results to UI state | Imports widgets other than `TextEditingController` and similar; knows URLs |
| Repository | Hides where data comes from; converts DTOs to models; maps errors | Shows dialogs or snackbars; navigates |
| API service / storage | Raw HTTP or disk access | Contains business rules |

### Patterns to use

| Pattern | Use it for | Example |
|---|---|---|
| Repository | Hiding API and storage behind one interface | `abstract interface class BookingRepository` |
| Dependency injection | Giving a class what it needs from outside | Constructor parameters plus bindings |
| Strategy / interface | Swapping implementations (real, fake, demo) | `ApiAuthRepository` and `FakeAuthRepository` |
| Interceptor | Cross-cutting HTTP work: auth header, refresh, logging | Dio `Interceptor` |
| Sealed UI state | One value describing what the screen shows | `Loading`, `Loaded`, `Failed` |
| Facade | One simple entry point over a messy subsystem | `PaymentGateway` over several payment SDKs |

### Example: an interface you can swap

```dart
// data/auth_repository.dart
abstract interface class AuthRepository {
  Future<User> login(String identifier, String password);
  Future<void> logout();
}

// data/api_auth_repository.dart
final class ApiAuthRepository implements AuthRepository {
  ApiAuthRepository(this._api, this._tokens);

  final AuthApi _api;
  final TokenStore _tokens;

  @override
  Future<User> login(String identifier, String password) => guardApi(() async {
        final res = await _api.login(identifier, password);
        await _tokens.save(access: res.accessToken, refresh: res.refreshToken);
        return res.user.toModel();
      });

  @override
  Future<void> logout() => guardApi(() async {
        await _api.logout();
        await _tokens.clear();
      });
}

// test/fakes/fake_auth_repository.dart
final class FakeAuthRepository implements AuthRepository {
  @override
  Future<User> login(String identifier, String password) async =>
      password == 'secret' ? const User(id: 1, name: 'Test') : throw const InvalidCredentials();

  @override
  Future<void> logout() async {}
}
```

The controller depends on `AuthRepository`, so tests, demos and the real app use the same controller.

### Anti-patterns to remove

- **God class.** One helper that shows dialogs, encrypts text, formats dates and checks the network. Split it by job: `Dialogs`, `Crypto`, `DateFormatters`, `Connectivity`.
- **Copy-paste error handling.** The same `try / on DioException / catch` block in every repository method. Write it once (see section 9).
- **Two state systems on one screen.** `setState` and a controller both changing the same data. Pick one owner.

---

## 6. State management

**Audience:** Beginner, Junior, Senior

> **In plain words:** "State" is everything the screen needs to remember right now: which seats are picked, whether it is loading, what error to show. State management is the rule for who owns that memory and how the screen finds out it changed.

This guide says **controller** for whatever object holds a screen's state: a `GetxController` (GetX), a `ChangeNotifier` (Provider), a `Notifier` (Riverpod) or a `Cubit` / `Bloc` (Bloc). Every rule applies to all four. Where the code differs, an example is shown for each.

### Choosing an approach

| | GetX | Provider | Riverpod | Bloc / Cubit |
|---|---|---|---|---|
| What it is | State, dependency injection and navigation in one package | Flutter's original recommended approach, built on `InheritedWidget` | Compile-safe successor to Provider, by the same author | Events or method calls in, states out, over streams |
| State lives in | `GetxController` + `.obs` | `ChangeNotifier` | `Notifier` / `AsyncNotifier` | `Cubit` / `Bloc` |
| UI listens with | `Obx`, `GetBuilder` | `context.watch`, `Consumer`, `Selector` | `ref.watch`, `ConsumerWidget` | `BlocBuilder`, `BlocListener`, `BlocSelector` |
| Dependency injection | `Get.put`, `Bindings` | `Provider` above the screen | Providers, overridable in tests | `RepositoryProvider`, `BlocProvider` |
| Navigation | Built in (`Get.toNamed`) | `go_router` | `go_router` | `go_router` |
| Learning curve | Easiest | Easy | Medium | Steeper |
| Testability | Fair (global access) | Good | Excellent | Excellent |
| Boilerplate | Very little | Little | Little to medium | More |

How to decide:

1. **Existing app:** keep what it already uses. One consistent approach beats a half-finished migration.
2. **New app, most teams:** Riverpod. It catches mistakes at compile time, is easy to test, and doesn't need a `BuildContext` to read state.
3. **Large team, strict reviews, complex flows such as payments:** Bloc. Every change goes through an explicit method or event, so behaviour is predictable and easy to trace.
4. **Small app, or learning Flutter:** Provider. It has the fewest new ideas.
5. **Team already fluent in GetX that needs to ship fast:** GetX is fine, but follow section 7 strictly (constructor injection) so the app stays testable and can migrate later.

**MUST** use one approach per project and name it in the README. Mixing `setState`, GetX and `ChangeNotifier` for the same data is the most common cause of "the screen didn't update" bugs.

### Rules

- **MUST** keep business state in controllers, not in widgets.
- **MUST** use `setState` only for purely visual, local state (an expanded tile, a hover). If a controller exists for the screen, the controller owns the data.
- **MUST** dispose everything a controller creates: in `onClose()` (GetX), `dispose()` (ChangeNotifier), `close()` (Bloc) or `ref.onDispose` (Riverpod). That includes `TextEditingController`, `ScrollController`, `FocusNode`, `Timer` and `StreamSubscription`.
- **SHOULD** model screen status as one value, not several booleans that can contradict each other.
- **SHOULD** use enums or sealed classes instead of magic strings (`TicketType.local`, not `'local'`).
- **SHOULD** rebuild only the widget that changes: `Obx` around one widget (GetX), `context.select` or `Selector` (Provider), `ref.watch(provider.select(...))` (Riverpod), `BlocSelector` or `buildWhen` (Bloc).
- **AVOID** reading global objects deep inside widgets (`Get.find`, `Get.context`, `GetIt.I`). Pass widgets what they need, or read it once at the top of the screen.

### One sealed state, in every approach

Bad: flags that can disagree.

```dart
bool isLoading = false;
bool hasError = false;
List<Trip> trips = []; // what if isLoading AND hasError are both true?
```

Good: one sealed state. This part is plain Dart and is the same in every approach.

```dart
sealed class TripsState {
  const TripsState();
}
final class TripsLoading extends TripsState {
  const TripsLoading();
}
final class TripsLoaded extends TripsState {
  const TripsLoaded(this.trips);
  final List<Trip> trips;
}
final class TripsFailed extends TripsState {
  const TripsFailed(this.message);
  final String message;
}
```

The controller that loads trips, in each approach:

<!-- tabs -->

**GetX**

```dart
class TripsController extends GetxController {
  TripsController(this._repo);
  final TripRepository _repo;

  final state = Rx<TripsState>(const TripsLoading());

  Future<void> load(TripSearch search) async {
    state.value = const TripsLoading();
    state.value = switch (await _repo.search(search)) {
      Ok(:final value) => TripsLoaded(value),
      Err(:final failure) => TripsFailed(failure.userMessage),
    };
  }
}

// In the screen: rebuild only this part
Obx(() => TripsView(state: controller.state.value));
```

**Provider**

```dart
class TripsNotifier extends ChangeNotifier {
  TripsNotifier(this._repo);
  final TripRepository _repo;

  TripsState _state = const TripsLoading();
  TripsState get state => _state;

  Future<void> load(TripSearch search) async {
    _state = const TripsLoading();
    notifyListeners();
    _state = switch (await _repo.search(search)) {
      Ok(:final value) => TripsLoaded(value),
      Err(:final failure) => TripsFailed(failure.userMessage),
    };
    notifyListeners();
  }
}

// In the screen: listen to this one field only
final state = context.select((TripsNotifier n) => n.state);
return TripsView(state: state);
```

**Riverpod**

```dart
final tripsProvider =
    NotifierProvider<TripsNotifier, TripsState>(TripsNotifier.new);

class TripsNotifier extends Notifier<TripsState> {
  @override
  TripsState build() => const TripsLoading();

  Future<void> load(TripSearch search) async {
    state = const TripsLoading();
    state = switch (await ref.read(tripRepositoryProvider).search(search)) {
      Ok(:final value) => TripsLoaded(value),
      Err(:final failure) => TripsFailed(failure.userMessage),
    };
  }
}

// In the screen (a ConsumerWidget)
final state = ref.watch(tripsProvider);
return TripsView(state: state);
```

**Bloc**

```dart
class TripsCubit extends Cubit<TripsState> {
  TripsCubit(this._repo) : super(const TripsLoading());
  final TripRepository _repo;

  Future<void> load(TripSearch search) async {
    emit(const TripsLoading());
    emit(switch (await _repo.search(search)) {
      Ok(:final value) => TripsLoaded(value),
      Err(:final failure) => TripsFailed(failure.userMessage),
    });
  }
}

// In the screen
BlocBuilder<TripsCubit, TripsState>(
  builder: (context, state) => TripsView(state: state),
);
```

<!-- /tabs -->

The widget that draws the state is identical in all four, because it only receives a `TripsState`. The compiler makes you handle every case:

```dart
class TripsView extends StatelessWidget {
  const TripsView({super.key, required this.state});
  final TripsState state;

  @override
  Widget build(BuildContext context) => switch (state) {
        TripsLoading() => const TripListShimmer(),
        TripsLoaded(:final trips) => TripList(trips: trips),
        TripsFailed(:final message) => ErrorMessage(message: message),
      };
}
```

Riverpod tip: when a screen only has loading, data and error states, `AsyncNotifier` and `AsyncValue` give you those three for free, so you don't need your own sealed class.

---

## 7. Dependency injection

**Audience:** Junior, Senior

> **In plain words:** A class should be handed its tools, not go looking for them. Then in a test you can hand it pretend tools.

Rules:

- **MUST** receive dependencies through the constructor (in Riverpod, through `ref` inside the provider).
- **MUST** register dependencies in one place per feature, plus one place for app-wide services: GetX bindings, a `Provider` or `RepositoryProvider` above the route, or Riverpod providers.
- **MUST NOT** create or look up dependencies in class field initialisers (`= Get.put(...)`, `= Get.find()`, `= GetIt.I<...>()`, `= ApiAuthRepository()`). It hides what a class needs and makes it impossible to replace in tests.
- **SHOULD** register against the interface (`AuthRepository`), not the implementation.
- **SHOULD** scope feature objects to their route. Keep only true app-wide services (HTTP client, session) alive for the whole app.

Bad: hidden dependencies that can't be replaced in tests. GetX is shown; the same mistake happens in any approach.

```dart
class LoginController extends GetxController {
  final AuthService _authService = Get.put(AuthService()); // creates a new one every time
}

class AuthService {
  final AuthRepository _repo = Get.put(AuthRepository());
  final TokenStorage _tokens = Get.put(TokenStorage());
}
```

Good: dependencies are visible and replaceable.

<!-- tabs -->

**GetX**

```dart
class LoginController extends GetxController {
  LoginController(this._auth);
  final AuthRepository _auth;
}

// App-wide, once (AppBinding)
Get.put<AuthRepository>(ApiAuthRepository(api, tokens), permanent: true);

// Per feature (LoginBinding)
class LoginBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(() => LoginController(Get.find<AuthRepository>()));
  }
}
```

**Provider**

```dart
class LoginNotifier extends ChangeNotifier {
  LoginNotifier(this._auth);
  final AuthRepository _auth;
}

// App-wide, once (main.dart)
Provider<AuthRepository>(
  create: (_) => ApiAuthRepository(api, tokens),
  child: const MyApp(),
);

// Per feature (around the login screen)
ChangeNotifierProvider(
  create: (context) => LoginNotifier(context.read<AuthRepository>()),
  child: const LoginScreen(),
);
```

**Riverpod**

```dart
final authRepositoryProvider = Provider<AuthRepository>(
  (ref) => ApiAuthRepository(ref.watch(authApiProvider), ref.watch(tokenStoreProvider)),
);

final loginProvider =
    NotifierProvider<LoginNotifier, LoginState>(LoginNotifier.new);

class LoginNotifier extends Notifier<LoginState> {
  AuthRepository get _auth => ref.read(authRepositoryProvider);

  @override
  LoginState build() => const LoginIdle();
}

// In tests
ProviderScope(
  overrides: [authRepositoryProvider.overrideWithValue(FakeAuthRepository())],
  child: const MyApp(),
);
```

**Bloc**

```dart
class LoginCubit extends Cubit<LoginState> {
  LoginCubit(this._auth) : super(const LoginIdle());
  final AuthRepository _auth;
}

// App-wide, once (main.dart)
RepositoryProvider<AuthRepository>(
  create: (_) => ApiAuthRepository(api, tokens),
  child: const MyApp(),
);

// Per feature (around the login screen)
BlocProvider(
  create: (context) => LoginCubit(context.read<AuthRepository>()),
  child: const LoginScreen(),
);
```

<!-- /tabs -->

In every approach, tests swap `ApiAuthRepository` for `FakeAuthRepository` in exactly one place: the binding, the provider, or a Riverpod override.

---

## 8. Navigation and routes

**Audience:** Beginner, Junior, Senior

GetX has its own router. Provider, Riverpod and Bloc apps normally use **go_router**, the routing package published by the Flutter team.

- **MUST** keep route names or paths as constants in one file (`AppRoutes.checkout`), never as typed strings in screens.
- **SHOULD** pass arguments as a typed class, not a `Map`:

```dart
final class CheckoutArgs {
  const CheckoutArgs({required this.trip, required this.seats, required this.holdUntil});
  final Trip trip;
  final List<Seat> seats;
  final DateTime holdUntil;
}
```

<!-- tabs -->

**GetX**

```dart
// Route table: read the arguments once, pass them into the controller
GetPage(
  name: AppRoutes.checkout,
  page: () => const CheckoutScreen(),
  binding: BindingsBuilder(() {
    final args = Get.arguments as CheckoutArgs;
    Get.lazyPut(() => CheckoutController(args, Get.find()));
  }),
);

// Navigate
Get.toNamed(AppRoutes.checkout, arguments: CheckoutArgs(trip: t, seats: s, holdUntil: h));
```

**go_router (Provider, Riverpod, Bloc)**

```dart
// Route table
final router = GoRouter(
  redirect: (context, state) => authGuard(context, state), // login guard
  routes: [
    GoRoute(
      path: AppRoutes.checkout,
      builder: (context, state) => CheckoutScreen(args: state.extra! as CheckoutArgs),
    ),
  ],
);

// Navigate
context.push(AppRoutes.checkout, extra: CheckoutArgs(trip: t, seats: s, holdUntil: h));
```

<!-- /tabs -->

- **SHOULD** remember that go_router's `extra` is lost when the app opens from a link or the web page reloads. Put IDs that must survive in the path (`/checkout/:bookingId`) and load the rest.
- **SHOULD** use route guards for login-required pages instead of checking in each screen: `GetMiddleware` (GetX) or `redirect` (go_router).
- **MUST** allow-list deep links and validate their parameters before navigating.
- **AVOID** one screen reaching into another screen's controller to refresh it (`Get.find<OtherController>()`, `context.read<OtherCubit>()`). Use a shared repository or an event stream instead.

---

## 9. Networking and API calls

**Audience:** Junior, Senior

> **In plain words:** All talk with the server goes through one well-guarded door. That door adds the login token, retries when the token expires, gives up after a timeout, and turns any failure into a message a person can understand.

Rules:

- **MUST** create one HTTP client for the app (one Dio), configured in one place.
- **MUST** read the base URL from configuration (`--dart-define` or flavors). **MUST NOT** edit generated files such as `api_service.g.dart` to change URLs. If two files must be edited to switch servers, the design is wrong.
- **MUST** set connect, send and receive timeouts.
- **MUST** use HTTPS outside local development.
- **MUST** enable request logging only in debug builds, and never log tokens or passwords.
- **SHOULD** use typed APIs (Retrofit, or a thin typed wrapper). Return models, not `Map<String, dynamic>`.
- **SHOULD** refresh tokens in an interceptor with a single-flight lock, so ten parallel 401s cause one refresh.
- **SHOULD** decode large JSON off the UI thread (`dio.transformer = BackgroundTransformer();` or `compute`).
- **SHOULD** cancel requests when the user leaves the screen (`CancelToken`).

Config that can't be misconfigured:

```dart
abstract final class AppConfig {
  static const apiBaseUrl = String.fromEnvironment('API_BASE_URL');
  static const apiTimeout = Duration(seconds: 20);
}

// flutter run --dart-define=API_BASE_URL=https://api.example.com/v1/
// or: flutter run --dart-define-from-file=env/dev.json
```

Handle errors once, at the repository boundary:

```dart
sealed class Result<T> {
  const Result();
}
final class Ok<T> extends Result<T> {
  const Ok(this.value);
  final T value;
}
final class Err<T> extends Result<T> {
  const Err(this.failure);
  final AppFailure failure;
}

Future<Result<T>> guardApi<T>(Future<T> Function() call) async {
  try {
    return Ok(await call());
  } on DioException catch (e) {
    return Err(AppFailure.fromDio(e)); // timeout, offline, 401, 422 field errors, 500
  } on FormatException catch (e) {
    return Err(AppFailure.badResponse(e));
  }
}

// Each repository method becomes one line:
Future<Result<List<Trip>>> search(TripSearch s) =>
    guardApi(() async => (await _api.searchTrips(s.toQuery())).data.map((d) => d.toModel()).toList());
```

`AppFailure` holds a user message key (for translation) and the technical detail (for logs). The UI shows the first; crash reporting gets the second.

---

## 10. Models and data

**Audience:** Beginner, Junior, Senior

- **MUST** make models immutable: `final` fields and `const` constructors.
- **MUST** be honest about nulls. If the server can omit a field, it is nullable or has a default; never `!` your way past it.
- **SHOULD** generate JSON code (`json_serializable`, `freezed`) instead of hand-writing `fromJson`.
- **SHOULD** use enums with `@JsonValue` for fixed server values.
- **SHOULD** implement value equality (`==` and `hashCode`, `equatable`, or `freezed`) for models compared in state.
- **SHOULD** separate the API shape (DTO / response) from the app model when the server shape is awkward. Convert in the repository.
- **MUST** decide whether generated `*.g.dart` files are committed, write it in the README, and run `dart run build_runner build --delete-conflicting-outputs` after changing a model.

```dart
@JsonSerializable()
final class SeatDto {
  const SeatDto({required this.number, required this.status, this.price});

  final String number;
  final SeatStatus status;
  final int? price; // optional on the server: nullable here

  factory SeatDto.fromJson(Map<String, dynamic> json) => _$SeatDtoFromJson(json);
}

enum SeatStatus {
  @JsonValue('available') available,
  @JsonValue('booked') booked,
  @JsonValue('blocked') blocked,
}
```

---

## 11. UI, widgets and design system

**Audience:** Beginner, Junior, Senior

> **In plain words:** Build the app from a box of standard Lego pieces (buttons, fields, cards). Every screen uses the same pieces, so the app looks consistent and a change to a piece updates it everywhere.

### Widgets

- **SHOULD** keep screen files under about 400 lines and `build` methods under about 80 lines.
- **SHOULD** extract parts into small `StatelessWidget` classes, not methods that return widgets. Classes can be `const`, skip rebuilds, and show up in DevTools.
- **MUST** use `const` constructors wherever possible.
- **SHOULD** put a widget in `core/widgets/` as soon as a second feature needs it.

```dart
// AVOID: a method. Rebuilt every time the parent rebuilds.
Widget _seatLegend() => Row(children: [...]);

// PREFER: a class. Can be const and skipped by the framework.
class SeatLegend extends StatelessWidget {
  const SeatLegend({super.key});
  @override
  Widget build(BuildContext context) => const Row(children: [/* ... */]);
}
```

### Design tokens

- **MUST** take colors, text styles and shapes from `Theme.of(context)` or a token class (`AppColors.brand`), never `Color(0xFF...)` inside a screen.
- **SHOULD** define spacing constants (`AppSpacing.md = 16`) instead of scattered magic numbers.
- **SHOULD** support dark mode from the start, even if it ships later. It's cheap early and expensive late.

### Responsive layout

- **MUST** test every screen at 320 px wide (small phones) and at 200% text size.
- **SHOULD** use `LayoutBuilder`, `Flexible`, `Expanded`, `Wrap` and `MediaQuery.sizeOf(context)` instead of fixed widths.
- **AVOID** fixed heights on anything that contains text.

### Accessibility

- **MUST** give tap targets at least 48 × 48 dp.
- **MUST** label icon-only buttons (`tooltip:` or `Semantics(label:)`).
- **SHOULD** respect "reduce motion" (`MediaQuery.disableAnimationsOf(context)`) for auto-scrolling sliders and animations.
- **SHOULD** keep text contrast at 4.5 : 1 or more.

### Localisation

- **MUST NOT** hard-code user-visible text. Use translation keys (`'search_bus'.tr` or ARB / `AppLocalizations`).
- **SHOULD** keep translations in JSON or ARB files, not giant Dart maps, so translators can edit them.
- **MUST** format money, dates and numbers with `intl` for the current locale.

---

## 12. Performance

**Audience:** Junior, Senior (the table is readable by everyone)

> **In plain words:** The phone redraws the screen 60 to 120 times a second. If any redraw takes longer than about 16 milliseconds, the user sees a stutter. Performance work means doing less on each redraw and doing heavy work somewhere else.

| Rule | Why | How |
|---|---|---|
| Use `const` widgets | Flutter skips rebuilding them | `const Text('...')`, `const SizedBox(height: 8)` |
| Rebuild the smallest part | Less work per frame | `Obx` around one widget, `Selector`, `ref.watch(p.select(...))`, `BlocSelector` |
| Build long lists lazily | Only visible rows are built | `ListView.builder`, `SliverList`, pagination |
| No heavy work in `build` | `build` can run every frame | Compute in the controller; cache results |
| Decode JSON off the UI thread | Big responses freeze the UI | `BackgroundTransformer`, `compute()`, `Isolate.run` |
| Size and cache images | Full-size decodes waste memory | `cacheWidth`, `cached_network_image`, WebP assets |
| Dispose resources | Leaks slow the app over time | Cancel timers, close streams, dispose controllers |
| Give list items keys | Correct reuse when the list changes | `ValueKey(item.id)` |
| Keep dependencies lean | Every package adds size and startup time | Review `pubspec.yaml` each release; remove unused ones |
| Load big data lazily | Faster start-up | JSON asset loaded on first use, not a 3,000-line Dart constant |
| Measure, don't guess | Your guess about the bottleneck is often wrong | DevTools in **profile** mode on a real low-end phone |

Budgets to agree on and check before each release:

- Cold start to first screen: under 2 seconds on a mid-range Android phone.
- No frame over 16 ms during scroll on the main lists.
- Release APK size tracked per release; investigate any jump over 10%.

---

## 13. Security

**Audience:** Everyone (rules), Senior (enforcement)

> **In plain words:** Anything inside the app can be read by anyone who downloads it. So the app must never carry the keys to the company safe. Those stay on the server.

- **MUST NOT** put API secrets, encryption keys, signing passwords or admin tokens in source code. Anyone can extract them from the built app. If one was ever committed, **rotate it**; deleting the line is not enough, because git history keeps it.
- **MUST NOT** store the user's password on the device, not even encrypted. "Remember me" means remembering the *username* and keeping a *refresh token*.
- **MUST** store tokens in secure storage (`flutter_secure_storage`: Keychain / Keystore), not in plain key-value storage.
- **MUST NOT** commit machine-specific or secret files: `local.properties`, `key.properties`, `*.jks`, `.env`. Add them to `.gitignore`.
- **MUST** use HTTPS. Consider certificate pinning for payment flows.
- **MUST** turn off verbose network logging in release builds.
- **MUST** validate deep link paths and parameters against an allow-list.
- **SHOULD** build releases with `--obfuscate --split-debug-info=build/symbols`.
- **SHOULD** strip personal data (phone, NRC, names) from crash reports and logs.
- **SHOULD** run payment pages in a WebView restricted to the payment provider's domains, and confirm payment status with the server, never from the WebView URL alone.

---

## 14. Errors, logging and monitoring

**Audience:** Junior, Senior

- **MUST NOT** swallow errors: `catch (_) {}` hides bugs. At minimum, log them.
- **MUST** show the user a clear, translated message and a way forward (Retry, Go back, Contact support).
- **SHOULD** use one logger with levels (`debug`, `info`, `warning`, `error`) instead of `print`; debug output is compiled out of release builds.
- **SHOULD** report unexpected errors to a crash reporter (Firebase Crashlytics, Sentry) with breadcrumbs, but without personal data.
- **SHOULD** set `FlutterError.onError` and `PlatformDispatcher.instance.onError` in `main` so no crash goes unreported.

| Failure | User sees | Developer gets |
|---|---|---|
| No internet | "You're offline. Check your connection." + Retry | Nothing (expected) |
| Timeout | "The server is slow. Try again." + Retry | Breadcrumb |
| 401 after refresh failed | Sent to login with "Please sign in again" | Breadcrumb |
| 422 validation | Field-level messages under each input | Nothing (expected) |
| 500 or parse error | "Something went wrong. We've been notified." | Crash report with request path |

---

## 15. Configuration and environments

**Audience:** Junior, Senior

- **MUST** have one source of truth per environment (dev, staging, production). Switching environments **MUST NOT** need code edits.
- **SHOULD** use flavors for things the OS must know (app ID, app name, icon) and `--dart-define-from-file` for values the Dart code reads.
- **MUST** pin the Flutter SDK version (`.fvmrc` or the README) and use it in CI. Different SDK versions on different machines produce "works on my machine" bugs and broken test runs.

```text
env/
├── dev.json       {"API_BASE_URL": "https://dev-api.example.com/v1/"}
├── staging.json   {"API_BASE_URL": "https://staging-api.example.com/v1/"}
└── prod.json      {"API_BASE_URL": "https://api.example.com/v1/"}
```

```bash
flutter run   --flavor dev  --dart-define-from-file=env/dev.json
flutter build appbundle --flavor prod --dart-define-from-file=env/prod.json --obfuscate --split-debug-info=build/symbols
```

Secret values (signing passwords and similar) live in CI secrets, never in these files.

---

## 16. Testing

**Audience:** Everyone (why), Junior and Senior (how)

> **In plain words:** Tests are robots that use the app the way a customer would, every time someone changes the code. If a change breaks booking, the robot notices before the customer does.

```text
        ▲  few      Integration tests   whole app on a device: login → book → pay
       ▲▲▲          Widget tests        one screen or flow with fake data
     ▲▲▲▲▲▲▲  many  Unit tests          controllers, repositories, formatters, validators
```

| Layer | Test | Example |
|---|---|---|
| Utils / formatters | Unit | `formatKyat(15000)` gives `15,000 MMK` |
| Models | Unit | `SeatDto.fromJson` handles missing `price` |
| Repositories | Unit with a fake API | A 401 becomes `AppFailure.sessionExpired` |
| Controllers | Unit with a fake repository | Selecting more seats than passengers is refused |
| Screens and flows | Widget | Search → results → seats → checkout on a 320 px screen |
| Critical journeys | Integration | Real build on an emulator in CI before release |

Rules:

- **MUST** have automated tests for login, search, seat selection, checkout and payment result handling.
- **MUST** keep the test suite green. A failing test is fixed or deleted the same day, not ignored.
- **SHOULD** use fakes through interfaces (section 5) rather than hitting a real server.
- **SHOULD** test at a small screen size and with the second language, because layout bugs hide there.
- **SHOULD** name tests as sentences: `'refuses checkout when the seat hold has expired'`.

```dart
test('refuses checkout when the seat hold has expired', () async {
  final controller = CheckoutController(
    CheckoutArgs(trip: trip, seats: seats, holdUntil: DateTime.now().subtract(const Duration(seconds: 1))),
    FakeBookingRepository(),
  );

  final result = await controller.confirm();

  expect(result, isA<Err<Booking>>());
});
```

---

## 17. Git, code review and CI

**Audience:** Junior, Senior

- **SHOULD** use short-lived branches: `feature/user-profile`, `fix/token-refresh`.
- **SHOULD** keep commits small, each doing one thing, with a short subject in the imperative ("Add seat hold timer").
- **MUST** open a pull request for every change to `main`, reviewed by someone else.
- **MUST** have CI run on every pull request, and block merging if any step fails:

```bash
dart format --output=none --set-exit-if-changed .
flutter analyze                 # must be zero issues
flutter test --coverage
flutter build apk --debug       # proves it still compiles for the device
```

Reviewers check *design* first (right layer? reusable? safe?), then *correctness*, then *style*. The tools already check style.

---

## 18. Documentation

**Audience:** Everyone

Every project's `README.md` **MUST** answer:

1. What is this app and who is it for?
2. Which Flutter version, and how do I install it?
3. How do I run it against dev, staging and prod?
4. Where does each kind of code live? (a short folder map)
5. How do I add a new feature? (bindings, routes, translations, tests)
6. How do I build and release?

**SHOULD** record big decisions ("Why GetX?", "Why we don't store passwords") as short Architecture Decision Records in `docs/adr/`: context, decision, consequences. Half a page is enough.

---

<!-- HIDDEN: sections 19 to 21 (Checklists, Project scorecard, Case study). Delete this line and the matching closing line to show them again.
## 19. Checklists

**Audience:** Junior, Senior

### New feature

- [ ] Feature folder created with `screens/`, `state/`, `data/`, `models/`, `bindings/`
- [ ] Repository interface defined; real and fake implementations exist
- [ ] Route constant added (`GetPage` or `GoRoute`) with its dependencies registered; typed arguments class used
- [ ] All user text added to every translation file
- [ ] Colors and text styles come from the theme
- [ ] Loading, empty, error and success states all designed and handled
- [ ] Controllers dispose every controller, timer and subscription
- [ ] Unit tests for the controller; widget test for the main flow
- [ ] Checked at 320 px width, 200% text size and in the second language

### Pull request review

- [ ] `flutter analyze` shows zero issues; CI is green
- [ ] Each class does one job; no new god class or 400-plus-line file
- [ ] Dependencies arrive through constructors; no `Get.put`, `Get.find` or `GetIt.I` in fields
- [ ] No secrets, passwords, tokens or personal data in code or logs
- [ ] No commented-out code, `print`, or empty `catch`
- [ ] Errors reach the user as a clear message with a next step
- [ ] Lists are lazy; no heavy work in `build`
- [ ] Tests added or updated for the changed behaviour

### Release

- [ ] Version and build number bumped
- [ ] Built with the production flavor and env file
- [ ] Obfuscated, with symbols uploaded to the crash reporter
- [ ] Network logging off; HTTPS base URL verified
- [ ] Smoke-tested on a low-end Android phone and a recent iPhone
- [ ] Release notes written in every supported language

---

## 20. Project scorecard

**Audience:** Everyone (managers can run it with a developer in 30 minutes)

Score each line 0, 1 or 2. Maximum 24.

| # | Area | 0: Needs work | 1: Acceptable | 2: Excellent |
|---|---|---|---|---|
| 1 | Lint and format | Many analyzer issues | Under 20 issues | Zero issues, enforced in CI |
| 2 | Structure | Mixed or unclear folders | Feature folders, some leakage | Clean feature-first layout, consistent names |
| 3 | Layers | UI calls the API directly | Layers exist but leak | Clear UI / state / data separation |
| 4 | Dependency injection | Service locator everywhere | Mixed | Constructor injection plus bindings or providers |
| 5 | State | Mixed systems, string flags | One system, some flags | One system, sealed states, scoped rebuilds |
| 6 | Reuse and UI | Copy-pasted widgets, hard-coded colors | Some shared widgets | Shared component library and theme tokens |
| 7 | Networking | URLs in many places, no timeouts | Central client | Typed API, timeouts, refresh, mapped errors |
| 8 | Security | Secrets in source or stored passwords | Minor gaps | No secrets, secure token storage, release hardening |
| 9 | Performance | Large rebuilds, heavy `build` | Mostly fine | Measured, lazy lists, background JSON |
| 10 | Errors and monitoring | Swallowed errors, `print` | Messages shown | Mapped failures plus crash reporting |
| 11 | Tests | None or failing | Some passing tests | Critical flows covered, green in CI |
| 12 | Docs and config | Edit code to switch server | README covers run | Full README, env files, pinned SDK |

**Reading the score:** 20 to 24 is healthy. 14 to 19 is fine, but plan cleanup. Under 14, pay down debt before adding big features.

---

## 21. Case study: two real-world projects compared

**Audience:** Everyone

This guide was written after comparing two real Flutter apps in the same business domain. Both use GetX and Dio. Their names are left out; **Project A** is an early prototype and **Project B** is a live production app. Measurements were taken on 25 November 2026.

| Measure | Project A | Project B |
|---|---|---|
| Stage | Prototype (offline demo data) | Production (live customers and resellers) |
| Dart code (hand-written) | about 4,500 lines, 35 files | about 26,000 lines, 228 files |
| Features | Core search, booking flow and auth | 15 modules: booking, payment, partner tools, printing, notifications and more |
| `flutter analyze` | No issues | 107 issues (33 unused imports, 14 deprecated APIs) |
| `print` / `debugPrint` calls | 0 | 93 |
| Commented-out code lines | 0 | about 160 |
| `Get.find` / `Get.put` calls | 4 | 152 (8 are `Get.put` in class fields) |
| Dependencies in `pubspec.yaml` | 7 | about 60 |
| Tests | 3 broad flow tests (auth, main flow, responsive) | 18 focused tests on one feature, 2 failing |
| Secrets in source | None | API secret and encryption key committed |

### Scorecard result

| # | Area | Project A | Project B |
|---|---|---|---|
| 1 | Lint and format | 2 | 0 |
| 2 | Structure | 2 | 1 |
| 3 | Layers | 1 | 1 |
| 4 | Dependency injection | 2 | 0 |
| 5 | State | 1 | 1 |
| 6 | Reuse and UI | 2 | 1 |
| 7 | Networking | 1 | 2 |
| 8 | Security | 2 | 0 |
| 9 | Performance | 1 | 1 |
| 10 | Errors and monitoring | 1 | 1 |
| 11 | Tests | 1 | 1 |
| 12 | Docs and config | 2 | 1 |
| | **Total (of 24)** | **18** | **10** |

### What each does well

**Project A** shows the *code habits* to copy:

- Zero analyzer issues, no debug prints, no dead code.
- `abstract interface class AuthService` with a demo implementation: the real API can replace it without touching the controller.
- Constructor injection (`AuthController(this._service)`), with controllers registered in route bindings.
- Base URL from `--dart-define`, validated at start-up, with timeouts.
- Passwords are never written to disk.
- Controllers dispose timers and scroll controllers; the auto-scrolling logo slider respects "reduce motion".
- Translations in JSON assets; colors in one token class.

**Project B** shows the *production infrastructure* to copy:

- Typed Retrofit API instead of raw maps.
- Token refresh in a Dio interceptor with a single-flight future and a write lock, which is correct and hard to get right.
- `BackgroundTransformer` so JSON decoding doesn't block the UI.
- Crash reporting with breadcrumbs, flavors, deep-link allow-list, forced-upgrade wrapper.
- Per-module bindings and route middleware.

### What each should fix next

**Project A** (before connecting the real backend):

1. Split its two largest screens (839 and 775 lines) into widget files.
2. Use one state system: one checkout controller uses `ChangeNotifier` while the rest of the app uses GetX.
3. Replace string values (ticket type, passenger type, payment method) with enums.
4. Stop passing the demo data service through every route; register a repository interface in a binding.
5. Add sealed loading/error states and a `guardApi` error mapper before the first real API call.
6. Add unit tests for controllers next to the flow tests, and pin the SDK with `.fvmrc`.

**Project B** (in priority order):

1. **Security, now:** rotate the committed API secret and encryption key, move them out of source, stop saving the password for "remember me", move tokens to secure storage, and untrack `local.properties`.
2. Make the base URL come from flavor config only; never edit the generated API file.
3. Reach zero analyzer issues; remove `print` calls and commented-out code; enforce it in CI.
4. Replace `Get.put` in class fields with constructor injection plus bindings.
5. Split the 350-line helper god class (dialogs, crypto, network errors, formatting) and the 891-line main booking screen, which mixes `setState` with GetX.
6. Replace the repeated `try / on DioException / catch` in each repository with one `guardApi` helper.
7. Move a 3,411-line static data file to a JSON asset loaded on demand; prune unused packages.
8. Fix the two failing tests and add tests for login, checkout and the token refresh.

**Fair note:** Project A is six times smaller and has no live backend yet, so it's easier to keep clean. The lesson is not "one team is better". Project A's habits and Project B's infrastructure together make the standard this guide describes.


-->
---

## Glossary

**Audience:** Everyone

| Term | Meaning |
|---|---|
| API | The server's "menu" of requests the app can make |
| Binding | A place where a feature's objects are created and registered (GetX) |
| Bloc / Cubit | A state-management package: a Cubit exposes methods that emit new states; a Bloc turns events into states |
| Build method | The function that describes what a widget looks like right now |
| CI | Continuous integration: a server that runs checks on every change |
| Controller | The object that holds a screen's state and makes decisions (also called notifier, cubit or bloc) |
| `const` | Tells Flutter a widget never changes, so it can be reused for free |
| Dependency injection | Handing a class the objects it needs instead of letting it create them |
| Dio | A popular HTTP client package for Dart |
| DTO | Data transfer object: the exact shape the server sends |
| Flavor | A build variant (dev, prod) with its own app ID, name and settings |
| GetIt | A service locator package, often used with Provider or Bloc |
| GetX | A Flutter package for state, navigation and dependency injection |
| go_router | The Flutter team's routing package, used with Provider, Riverpod and Bloc |
| God class | One class that does too many unrelated jobs |
| i18n | Internationalization: preparing an app to support many languages and regions |
| Interceptor | Code that runs on every network request or response |
| Isolate | A separate Dart worker for heavy tasks, so the UI stays smooth |
| l10n | Localization: adding one specific language and region (text, dates, currency) |
| Lint / analyzer | A tool that flags risky or messy code automatically |
| Notifier | Riverpod's class that holds state and the methods that change it |
| Provider | Flutter's original recommended state package, built on `InheritedWidget` |
| Repository | The class that knows where data comes from and hides it from the rest of the app |
| Retrofit | A package that generates typed API code from annotations |
| Riverpod | A compile-safe successor to Provider, by the same author |
| Sealed class | A type with a fixed list of cases that the compiler makes you handle |
| State | What the screen needs to remember right now |
| Technical debt | Shortcuts that make future changes slower and riskier |
| Token / refresh token | Proof the user is logged in; the refresh token gets a new one when it expires |
| Widget | Any piece of Flutter UI, from a single letter to a whole screen |
