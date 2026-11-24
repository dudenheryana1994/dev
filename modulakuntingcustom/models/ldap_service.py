from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, MODIFY_ADD
import logging
import re

_logger = logging.getLogger(__name__)

LDAP_SERVER = '192.168.10.5'  # Ganti dengan alamat server LDAP
LDAP_USER = 'uid=integrasi,cn=users,dc=silk,dc=co,dc=id'  # DN untuk bind
LDAP_PASSWORD = 'r4h4s14-data'  # Password untuk bind
BASE_DN = 'dc=silk,dc=co,dc=id'  # Base DN untuk pencarian
GROUP_BASE_DN = 'cn=Groups,dc=silk,dc=co,dc=id'  # Basis grup LDAP 'ou=Groups,dc=example,dc=com', 'ou=Groups,dc=a17,dc=net'

GROUP_MAPPING = {
    '10mbps': 'cn=10mbps,' + GROUP_BASE_DN,
    '15mbps': 'cn=15mbps,' + GROUP_BASE_DN,
    '20mbps': 'cn=20mbps,' + GROUP_BASE_DN,
}


def connect_to_ldap():
    server = Server(LDAP_SERVER, get_info=ALL)
    conn = Connection(server, LDAP_USER, LDAP_PASSWORD, auto_bind=True)
    return conn


# Fungsi untuk membuat Organizational Unit (OU) untuk pengguna
def create_users_ou():
    conn = connect_to_ldap()
    ou_dn = f"ou=Users,ou=Accounts,{BASE_DN}"
    attributes = {
        'objectClass': ['organizationalUnit'],
        'ou': ['Users']
    }
    # Cek apakah OU 'Users' sudah ada
    conn.search(BASE_DN, '(ou=Users)')
    if conn.entries:
        _logger.info("OU 'Users' already exists in LDAP.")
        conn.unbind()
        return True  # OU sudah ada, tidak perlu dibuat lagi
    # Jika belum ada, tambahkan OU
    _logger.info(f"Creating OU 'Users' at {ou_dn}")
    conn.add(ou_dn, attributes=attributes)
    if conn.result['description'] != 'success':
        _logger.error(f"Failed to create OU 'Users': {conn.result}")
        conn.unbind()
        return False
    else:
        _logger.info(f"OU 'Users' created successfully at {ou_dn}")
        conn.unbind()
        return True


# Fungsi untuk menambahkan pengguna ke LDAP
def add_user_to_ldap(user):
    conn = connect_to_ldap()
    ou_dn = f"ou=Users,ou=Accounts,{BASE_DN}"
    dn = f"cn={user.username},{ou_dn}"

    attributes = {
        'objectClass': ['inetOrgPerson', 'top', 'posixAccount'],
        'cn': user.username,
        'sn': user.name.split()[-1],
        'mail': user.email,
        'uid': user.username,
        'uidNumber': str(10000 + user.id),
        'gidNumber': '1000',
        'homeDirectory': f'/home/{user.username}',
        'userPassword': user.password,
        'givenName': user.name.split()[0],
        'displayName': user.name,
        'employeeNumber': user.card
    }

    try:
        conn.add(dn, attributes=attributes)
        _logger.info(f"Added user {user.username} to LDAP")

        # Tambahkan pengguna ke grup berdasarkan access_rights
        group_dn = GROUP_MAPPING.get(user.access_rights)
        if group_dn:
            conn.modify(group_dn, {'memberUid': [
                        (MODIFY_ADD, [user.username])]})
            if conn.result['description'] == 'success':
                _logger.info(
                    f"Added user {user.username} to group {user.access_rights}")
            else:
                _logger.error(
                    f"Failed to add user {user.username} to group: {conn.result}")
        else:
            _logger.warning(
                f"No LDAP group found for access_rights {user.access_rights}")

    except Exception as e:
        _logger.error(f"Error adding user {user.username} to LDAP: {e}")
    finally:
        conn.unbind()


# Fungsi untuk memperbarui pengguna di LDAP
def update_user_in_ldap(user):
    conn = connect_to_ldap()

    # Coba ganti spasi dengan underscore dan gunakan format nama sederhana
    # Menghapus karakter khusus kecuali huruf, angka, dan dash
    sanitized_username = re.sub(r'[^\w-]', '', user.username).replace(' ', '')
    sanitized_name = re.sub(r'[^\w-]', '', user.name).replace(' ', '')

    old_dn = f"cn={user.username},ou=Users,ou=Accounts,{BASE_DN}"
    new_dn = f"cn={sanitized_name},ou=Users,ou=Accounts,{BASE_DN}"

    changes = {
        'mail': [(MODIFY_REPLACE, [user.email])],
        'userPassword': [(MODIFY_REPLACE, [user.password])],
        'uid': [(MODIFY_REPLACE, [sanitized_username])],
        'cn': [(MODIFY_REPLACE, [sanitized_name])],
        'employeeNumber': [(MODIFY_REPLACE, [user.employee_number])]
    }

    # Log DN yang digunakan untuk debugging
    _logger.info(
        f"Updating user with old DN: {old_dn} and new DN: {new_dn} and changes: {changes}")

    conn.search(BASE_DN, f'(cn={user.username})',
                attributes=['cn', 'mail', 'uid'])

    if conn.entries:
        # Jika 'cn' berubah, kita perlu mengubah DN user
        if old_dn != new_dn:
            # Pindahkan user ke DN baru (rename)
            conn.modify_dn(old_dn, f'cn={sanitized_name}')
            if conn.result['description'] != 'success':
                _logger.error(
                    f"Failed to rename user {user.username} in LDAP: {conn.result}")
                conn.unbind()
                return

        # Lakukan modifikasi atribut lainnya
        conn.modify(new_dn, changes)
        if conn.result['description'] != 'success':
            _logger.error(
                f"Failed to update user {user.username} in LDAP: {conn.result}")
        else:
            _logger.info(f"User {user.username} updated successfully.")
    else:
        _logger.warning(f"User {user.username} not found in LDAP for update.")

    conn.unbind()


# Fungsi untuk mengambil pengguna dari LDAP
def get_ldap_users():
    conn = connect_to_ldap()
    conn.search(BASE_DN, '(objectClass=inetOrgPerson)',
                attributes=['cn', 'uid', 'mail'])
    ldap_users = conn.entries
    conn.unbind()
    return ldap_users


# Fungsi untuk menyinkronkan pengguna dari LDAP ke Odoo
def sync_ldap_users_to_odoo(env):
    ldap_users = get_ldap_users()

    # Ambil semua pengguna Odoo beserta username untuk pengecekan cepat
    existing_users = env['modulakuntingcustom.user'].search([])
    existing_usernames = existing_users.mapped('username')

    # Set untuk menyimpan uid dari pengguna LDAP
    ldap_uids = {user.uid for user in ldap_users}

    for ldap_user in ldap_users:
        # Cari pengguna yang sudah ada berdasarkan username (uid) di Odoo
        existing_user = env['modulakuntingcustom.user'].search(
            [('username', '=', ldap_user.uid)], limit=1)

        if not existing_user:
            # Jika tidak ditemukan, buat pengguna baru di Odoo
            new_user = env['modulakuntingcustom.user'].create({
                'username': ldap_user.uid,
                'name': ldap_user.cn,
                'email': ldap_user.mail,
                'password': 'default_password'  # Sesuaikan password
            })
            _logger.info(f"Created new user {ldap_user.uid} in Odoo.")
        else:
            # Jika pengguna ditemukan, cek apakah ada perbedaan yang perlu diperbarui
            needs_update = False

            # Cek apakah ada perubahan di nama atau email
            if existing_user.name != ldap_user.cn:
                existing_user.name = ldap_user.cn
                needs_update = True

            if existing_user.email != ldap_user.mail:
                existing_user.email = ldap_user.mail
                needs_update = True

            # Perbarui pengguna jika diperlukan
            if needs_update:
                existing_user.sudo().write({
                    'name': ldap_user.cn,
                    'email': ldap_user.mail
                })
                _logger.info(f"Updated user {ldap_user.uid} in Odoo.")
            else:
                _logger.info(
                    f"No changes for user {ldap_user.uid}, skipping update.")

    # Optional: Hapus pengguna di Odoo yang tidak ada di LDAP
    for odoo_user in existing_users:
        if odoo_user.username not in ldap_uids:
            odoo_user.unlink()
            _logger.info(
                f"Deleted user {odoo_user.username} from Odoo as it no longer exists in LDAP.")


# Fungsi untuk menghapus pengguna dari LDAP
def delete_user_from_ldap(user):
    conn = connect_to_ldap()
    # Gunakan DN yang sudah disanitasi yang sesuai dengan yang digunakan saat pengeditan
    sanitized_name = re.sub(r'[^\w-]', '', user.name)
    sanitized_name = sanitized_name.replace(' ', '')
    dn = f"cn={sanitized_name},ou=Users,ou=Accounts,{BASE_DN}"

    # Check if the user exists in LDAP before deleting
    conn.search(BASE_DN, f'(cn={sanitized_name})')
    if conn.entries:
        _logger.info(f"Deleting user {sanitized_name} from LDAP with DN: {dn}")
        conn.delete(dn)
        if conn.result['description'] != 'success':
            _logger.error(
                f"Failed to delete user {sanitized_name} from LDAP: {conn.result}")
        else:
            _logger.info(
                f"User {sanitized_name} deleted from LDAP successfully.")
    else:
        _logger.warning(
            f"User {sanitized_name} not found in LDAP for deletion.")
    conn.unbind()