<?php

/*
 * Sets Snipe-IT up for bbe, with Snipe-IT's own code, on its own image:
 * - setup: creates its own admin and its first settings, as its setup page would, so nobody has to go through it. Then
 *   signs people in against bbe-auth's LDAP, and runs the people part below.
 * - people: Snipe-IT creates people on their first sign-in, so this keeps exactly authentik's `admins` in Snipe-IT's
 *   `admins` group, which can do everything, among the people it created from LDAP.
 *
 * It reads before it writes, so a second run changes nothing.
 */

declare(strict_types=1);

require '/var/www/html/vendor/autoload.php';
$app = require '/var/www/html/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use App\Models\Group;
use App\Models\Setting;
use App\Models\User;
use Illuminate\Contracts\Encryption\DecryptException;
use Illuminate\Support\Facades\Crypt;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

const ADMIN_GROUP = 'admins';
const GROUPS = ['users', 'admins'];

function setting(string $name): string
{
    $value = getenv($name);
    if ($value === false || $value === '') {
        throw new RuntimeException("$name isn't set");
    }

    return $value;
}

function log_line(string $message): void
{
    fwrite(STDOUT, $message.PHP_EOL);
}

function group_dn(string $group): string
{
    return 'cn='.$group.',ou=groups,'.setting('LDAP_BASE_DN');
}

/**
 * A model's save that throws with its validation errors, rather than returning false
 */
function save($model, string $what): void
{
    if (! $model->save()) {
        throw new RuntimeException("Snipe-IT: couldn't save $what: ".$model->getErrors()->toJson());
    }
}

/**
 * Snipe-IT migrates its database as it starts. This waits until every migration in its image has run
 */
function wait_for_database(): void
{
    $deadline = time() + (int) setting('READY_TIMEOUT');
    $migrator = app('migrator');
    while (true) {
        try {
            if (! $migrator->repositoryExists()) {
                $waiting = 'its database to be created';
            } else {
                $files = array_keys($migrator->getMigrationFiles([database_path('migrations')]));
                $pending = array_diff($files, $migrator->getRepository()->getRan());
                if (! $pending) {
                    return;
                }
                $waiting = count($pending).' of its migrations';
            }
        } catch (Throwable $error) {
            DB::purge();
            $waiting = 'its database: '.$error->getMessage();
        }
        if (time() > $deadline) {
            throw new RuntimeException("Snipe-IT: gave up waiting for $waiting");
        }
        log_line("Snipe-IT: waiting for $waiting");
        sleep(5);
    }
}

/**
 * Snipe-IT's own admin, which isn't in LDAP, so it signs in with its own password when authentik can't help
 */
function own_admin(): User
{
    $username = setting('ADMIN_USERNAME');
    $password = setting('ADMIN_PASSWORD');
    $user = User::withTrashed()->where('username', $username)->first();
    if (! $user) {
        $user = new User;
        $user->username = $username;
        $user->first_name = 'Snipe-IT';
        $user->last_name = 'admin';
        $user->email = setting('ADMIN_EMAIL');
        $user->activated = 1;
        $user->permissions = json_encode(['superuser' => 1]);
        $user->password = bcrypt($password);
        save($user, "its admin $username");
        log_line("Snipe-IT: created its admin $username");

        return $user;
    }

    $changed = [];
    if ($user->trashed()) {
        $user->restore();
        $changed[] = 'restored';
    }
    if ((string) $user->activated !== '1') {
        $user->activated = 1;
        $changed[] = 'activated';
    }
    if (! $user->isSuperUser()) {
        $user->permissions = json_encode(['superuser' => 1]);
        $changed[] = 'made a superuser';
    }
    if (! Hash::check($password, $user->password)) {
        $user->password = bcrypt($password);
        $changed[] = "given bbe-misc-admin's password";
    }
    if ($changed) {
        save($user, "its admin $username");
        log_line("Snipe-IT: its admin $username was ".implode(', ', $changed));
    }

    return $user;
}

/**
 * The settings Snipe-IT's setup page saves with its first admin. Snipe-IT sends people to its setup page until there
 * are settings and someone in its database
 */
function first_settings(User $admin): void
{
    if (Setting::count() > 0) {
        return;
    }
    $settings = new Setting;
    $settings->site_name = setting('SITE_NAME');
    $settings->alert_email = $admin->email;
    $settings->alerts_enabled = 1;
    $settings->pwd_secure_min = 10;
    $settings->brand = 1;
    $settings->link_light_color = '#296282';
    $settings->link_dark_color = '#296282';
    $settings->nav_link_color = '#FFFFFF';
    $settings->locale = 'en-US';
    $settings->default_currency = setting('CURRENCY');
    $settings->created_by = $admin->id;
    $settings->next_auto_tag_base = 1;
    $settings->auto_increment_assets = 0;
    $settings->zerofill_count = 0;
    save($settings, 'its first settings');
    log_line('Snipe-IT: saved its first settings');
}

/**
 * Signing in against authentik's LDAP, for people in `users` or `admins`. Snipe-IT finds them with its own account, then
 * binds as them, and creates them in its database on their first sign-in. Their password isn't copied to Snipe-IT,
 * so someone authentik stops letting in can't sign in with the one they had
 */
function ldap_settings(): void
{
    $members = implode('', array_map(fn ($group) => '(memberOf='.group_dn($group).')', GROUPS));
    $wanted = [
        'ldap_enabled' => '1',
        // Plain LDAP inside the cluster, like Jellyfin's
        'ldap_server' => setting('LDAP_URL'),
        'ldap_tls' => '0',
        'ldap_server_cert_ignore' => '0',
        'is_ad' => '0',
        'ldap_uname' => setting('LDAP_BIND_DN'),
        'ldap_basedn' => setting('LDAP_BASE_DN'),
        // Snipe-IT wraps it in parentheses with the username's own condition, (<filter>(cn=<username>))
        'ldap_filter' => "&(objectClass=user)(|$members)",
        'ldap_auth_filter_query' => 'cn=',
        // Snipe-IT reads the attributes in lower case. authentik gives a person's whole name in displayName, which
        // goes in Snipe-IT's first name, its only required one
        'ldap_username_field' => 'cn',
        'ldap_fname_field' => 'displayname',
        'ldap_lname_field' => null,
        'ldap_email' => 'mail',
        'ldap_pw_sync' => '0',
        // authentik's LDAP can't change passwords, which people change in authentik
        'custom_forgot_pass_url' => setting('PASSWORD_RESET_URL'),
    ];

    $settings = Setting::getSettings();
    $changed = [];
    foreach ($wanted as $name => $value) {
        if ($settings->$name != $value || ($value === null) !== ($settings->$name === null)) {
            $settings->$name = $value;
            $changed[] = $name;
        }
    }
    try {
        $password = $settings->ldap_pword ? Crypt::decrypt($settings->ldap_pword) : null;
    } catch (DecryptException) {
        $password = null;
    }
    if ($password !== setting('LDAP_PASSWORD')) {
        $settings->ldap_pword = Crypt::encrypt(setting('LDAP_PASSWORD'));
        $changed[] = 'ldap_pword';
    }
    if ($changed) {
        save($settings, 'its LDAP settings');
        log_line('Snipe-IT: signs people in with bbe-auth\'s LDAP ('.implode(', ', $changed).')');
    }
}

/**
 * Snipe-IT's group that can do everything, which authentik's `admins` are kept in
 */
function admin_group(): Group
{
    $group = Group::where('name', ADMIN_GROUP)->first();
    if (! $group) {
        $group = new Group;
        $group->name = ADMIN_GROUP;
        $group->permissions = json_encode(['superuser' => '1']);
        $group->notes = 'authentik\'s admins, kept in this group by bbe';
        save($group, 'the admins group');
        log_line('Snipe-IT: created the admins group');
    } elseif (! (json_decode((string) $group->permissions, true)['superuser'] ?? null)) {
        $group->permissions = json_encode(['superuser' => '1']);
        save($group, 'the admins group');
        log_line('Snipe-IT: the admins group can do everything again');
    }

    return $group;
}

/**
 * The usernames of authentik's `admins`, in lower case
 */
function ldap_admins(): array
{
    $connection = ldap_connect(setting('LDAP_URL'));
    if (! $connection) {
        throw new RuntimeException('LDAP: couldn\'t connect to '.setting('LDAP_URL'));
    }
    ldap_set_option($connection, LDAP_OPT_PROTOCOL_VERSION, 3);
    ldap_set_option($connection, LDAP_OPT_REFERRALS, 0);
    ldap_set_option($connection, LDAP_OPT_NETWORK_TIMEOUT, 30);
    try {
        if (! @ldap_bind($connection, setting('LDAP_BIND_DN'), setting('LDAP_PASSWORD'))) {
            throw new RuntimeException('LDAP: couldn\'t bind as '.setting('LDAP_BIND_DN').': '.ldap_error($connection));
        }
        $results = @ldap_search(
            $connection,
            setting('LDAP_BASE_DN'),
            '(&(objectClass=user)(memberOf='.group_dn(ADMIN_GROUP).'))',
            ['cn'],
        );
        if (! $results) {
            throw new RuntimeException('LDAP: couldn\'t search for the admins: '.ldap_error($connection));
        }
        $entries = ldap_get_entries($connection, $results);
        $admins = [];
        for ($i = 0; $i < $entries['count']; $i++) {
            $admins[] = strtolower($entries[$i]['cn'][0]);
        }

        return $admins;
    } finally {
        ldap_unbind($connection);
    }
}

/**
 * Keeps exactly authentik's `admins` in Snipe-IT's `admins` group, among the people it created from LDAP. Its own admin
 * and people added in Snipe-IT itself are left alone
 */
function people(): void
{
    $group = admin_group();
    $admins = ldap_admins();
    foreach (User::where('ldap_import', 1)->get() as $user) {
        $wanted = in_array(strtolower($user->username), $admins, true);
        $member = $user->groups()->where('permission_groups.id', $group->id)->exists();
        if ($wanted && ! $member) {
            $user->groups()->attach($group->id);
            log_line("Snipe-IT: {$user->username} is an admin");
        } elseif (! $wanted && $member) {
            $user->groups()->detach($group->id);
            log_line("Snipe-IT: {$user->username} is no longer an admin");
        }
    }
}

try {
    wait_for_database();
    if (setting('MODE') === 'setup') {
        $admin = own_admin();
        first_settings($admin);
        ldap_settings();
        people();
        log_line('Snipe-IT: set up');
    } else {
        people();
        log_line('Snipe-IT: its admins are authentik\'s');
    }
} catch (Throwable $error) {
    fwrite(STDERR, $error->getMessage().PHP_EOL);
    exit(1);
}
