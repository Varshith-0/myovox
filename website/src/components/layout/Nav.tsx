import { NavLink, useLocation } from 'react-router-dom'
import { NAV_LINKS, SITE } from '@/data/site'
import { LogoMark } from '@/components/ui/LogoMark'
import styles from './Nav.module.css'

/**
 * Fixed, minimal top navigation present on every page. On the homepage the
 * hero *is* the brand lockup, so the nav shows only the links — the brand
 * appears here on every other page as the way back home.
 */
export function Nav() {
  const isHome = useLocation().pathname === '/'
  return (
    <header className={styles.nav}>
      {isHome ? (
        <span aria-hidden="true" />
      ) : (
        <NavLink to="/" className={styles.brand} aria-label={`${SITE.title} home`}>
          <LogoMark className={styles.mark} size={24} duration={12} />
          <span className={styles.wordmark}>{SITE.brand}</span>
        </NavLink>
      )}

      <nav className={styles.links} aria-label="Primary">
        {NAV_LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              isActive ? `${styles.link} ${styles.active}` : styles.link
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}
