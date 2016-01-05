from models import *
from app import app
import ldap

def authenticate_login(email, password):
    """

    :param email: Users email address
    :type email: string
    :param password: Users password
    :type password: string
    :return: The user object, if the user is authenticated, otherwise None
    :rtype: User object
    """
    if app.config['USE_LDAP'] == 'True':
        app.logger.info("Use LDAP: %s" % app.config['USE_LDAP'])
        # # Setup the LDAP Options
        if app.config['LDAP_USE_TLS']:
            # Sets up TLS for LDAP connection
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,
                            ldap.OPT_X_TLS_NEVER)
        if app.debug:
            # Sets up verbose logging for LDAP debugging
            ldap.set_option(ldap.OPT_DEBUG_LEVEL, 255)

        # Create the LDAP Context
        ctx = ldap.initialize('%s:%s' % (app.config['LDAP_SERVER'], app.config[
            'LDAP_PORT']))
        if app.config['LDAP_USE_TLS']:
            # Provide the certificate for LDAP, if required
            ctx.set_option(ldap.OPT_X_TLS_CACERTFILE, app.config['LDAP_CERT_PATH'])
        # Bind to LDAP Server
        try:
            ctx.bind_s(app.config['LDAP_SA_BIND_DN'], app.config[
                'LDAP_SA_PASSWORD'])
        except ldap.LDAPError as e:
            app.logger.error("Failed to bind to LDAP: %s", e)
            return None

        user = User.query.filter_by(email=email).first()
        if user and (user.is_staff or user.is_admin()):
            # check if user exists in LDAP
            user_dn = ctx.search_s(app.config['LDAP_BASE_DN'], ldap.SCOPE_SUBTREE,
                                   'mail=%s' % email)
            if user_dn and len(user_dn) == 1:
                # Bind as the user with the provided password
                try:
                    user_dn, attributes = user_dn[0]
                    authenticated = ctx.bind_s(user_dn, password)
                    app.logger.info("User: %s authenticated", user)
                    return user
                except ldap.INVALID_CREDENTIALS as e:
                    app.logger.info("User: %s failed to authenticate", user)
                    return None
            else:
                app.logger.info("User: %s not found", user)
                return None
        return None
    else:
        user = User.query.filter_by(email=email).first()
        if user and (user.is_staff or user.is_admin()):
            if user.check_password(password):
                return user
            if user.password == password:  # Hash it
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
            return user
        return None
