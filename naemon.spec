Summary:	Open Source Host, Service And Network Monitoring Program
Name:		naemon
Version:	0.8.0
Release:	0.1
License:	GPL v2
Group:		Applications/System
Source0:	http://labs.consol.de/naemon/release/v%{version}/src/%{name}-%{version}.tar.gz
URL:		http://www.naemon.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	chrpath
BuildRequires:	doxygen
BuildRequires:	expat-devel
BuildRequires:	gd
BuildRequires:	gd-devel >= 1.8
BuildRequires:	gperf
BuildRequires:	libjpeg-devel
BuildRequires:	libpng-devel
BuildRequires:	libtool
BuildRequires:	logrotate
BuildRequires:	mysql-devel
BuildRequires:	perl
BuildRequires:	perl-ExtUtils-MakeMaker
BuildRequires:	perl-Module-Install
BuildRequires:	perl-autodie
BuildRequires:	rsync
BuildRequires:	systemd
BuildRequires:	zlib-devel
Requires:	%{name}-core = %{version}-%{release}
Requires:	%{name}-livestatus = %{version}-%{release}
Requires:	%{name}-thruk = %{version}-%{release}
Requires:	%{name}-thruk-reporting = %{version}-%{release}

%description
Naemon is an application, system and network monitoring application.
It can escalate problems by email, pager or any other medium. It is
also useful for incident or SLA reporting. It is originally a fork of
Nagios, but with extended functionality, stability and performance.

It is written in C and is designed as a background process,
intermittently running checks on various services that you specify.

The actual service checks are performed by separate "plugin" programs
which return the status of the checks to Naemon. The plugins are
compatible with Nagios, and can be found in the monitoring-plugins
package.

Naemon ships the Thruk gui with extended reporting and dashboard
features.

%package core
Summary:	Naemon Monitoring Core
Group:		Applications/System
Requires:	logrotate


%description core
contains the %{name} core

%package livestatus
Summary:	Naemon Livestatus Eventbroker Module
Group:		Applications/System
Requires:	%{name}-core = %{version}-%{release}
Requires(post):	%{name}-core = %{version}-%{release}

%description livestatus
contains the %{name} livestatus eventbroker module

%package thruk
Summary:	Thruk Gui For Naemon
Group:		Applications/System
Requires:	%{name}-thruk-libs = %{version}-%{release}
Requires(preun):	%{name}-thruk-libs = %{version}-%{release}
Requires(post):	%{name}-thruk-libs = %{version}-%{release}
Requires:	gd
Requires:	httpd
Requires:	logrotate
Requires:	mod_fcgid
Requires:	perl
Requires:	wget
Conflicts:	thruk

%description thruk
This package contains the thruk gui for %{name}

%package thruk-libs
Summary:	Perl Librarys For Naemons Thruk Gui
Group:		Applications/System
Requires:	%{name}-thruk = %{version}-%{release}
Conflicts:	thruk

%description thruk-libs
This package contains the library files for the thruk gui

%package thruk-reporting
Summary:	Thruk Gui For Naemon Reporting Addon
Group:		Applications/System
Requires:	%{name}-thruk = %{version}-%{release}
Requires:	dejavu-fonts-common
Requires:	libXext
Requires:	xorg-x11-server-Xvfb

%description thruk-reporting
This package contains the reporting addon for naemons thruk gui useful
for sla and event reporting.

%package devel
Summary:	Development Files For Naemon
Group:		Development/Libraries

%description devel
This package contains the header files, static libraries and
development documentation for %{name}. If you are a NEB-module author
or wish to write addons for Naemon using Naemons own APIs, you should
install this package.

%prep
%setup -q

# Cleanup the environment, will cause autoreconf to get run
rm %{name}-core/configure
rm %{name}-livestatus/configure

%build
%configure \
	--with-initdir="%{_initrddir}" \
	--datadir="%{_datadir}/%{name}" \
	--libdir="%{_libdir}/%{name}" \
	--localstatedir="%{_localstatedir}/lib/%{name}" \
	--sysconfdir="%{_sysconfdir}/%{name}" \
	--enable-event-broker \
	--without-tests \
	--with-pluginsdir="%{_libdir}/%{name}/plugins" \
	--with-tempdir="%{_localstatedir}/cache/%{name}" \
	--with-checkresultdir="%{_localstatedir}/cache/%{name}/checkresults" \
	--with-logdir="%{_localstatedir}/log/%{name}" \
	--with-logrotatedir="%{_sysconfdir}/logrotate.d" \
	--with-naemon-user="naemon" \
	--with-naemon-group="naemon" \
	--with-lockfile="%{_localstatedir}/run/%{name}/%{name}.pid" \
	--with-thruk-user="http" \
	--with-thruk-group="naemon" \
	--with-thruk-libs="%{_libdir}/%{name}/perl5" \
	--with-thruk-tempdir="%{_localstatedir}/cache/%{name}/thruk" \
	--with-thruk-vardir="%{_localstatedir}/lib/%{name}/thruk" \
	--with-httpd-conf="%{_sysconfdir}/httpd/conf.d" \
	--with-htmlurl="/%{name}"

%{__make} all

%{__make} -C %{name}-core dox

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
    DESTDIR="$RPM_BUILD_ROOT" \
    INSTALL_OPTS="" \
    COMMAND_OPTS="" \
    INIT_OPTS=""

mv $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/thruk $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}-thruk
mv $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}-core

### Install documentation
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation/search
cp -a %{name}-core/Documentation/html/* $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation
chmod 0755 $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation/search
rm -f $RPM_BUILD_ROOT%{_datadir}/%{name}/documentation/installdox

# Put the new RC sysconfig in place
install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/
install -p %{name}-core/sample-config/%{name}.sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}

install -d $RPM_BUILD_ROOT%{_libdir}/%{name}/
ln -s %{_libdir}/nagios/plugins $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins

# Install systemd entry
install -D -p %{name}-core/daemon-systemd $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service
install -D -p %{name}-core/%{name}.tmpfiles.conf $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf
# Move SystemV init-script
#mv -f $RPM_BUILD_ROOT%{_initrddir}/%{name} $RPM_BUILD_ROOT%{_bindir}/%{name}-ctl

# Cleanup rpath errors in perl modules
chrpath --delete $RPM_BUILD_ROOT%{_libdir}/%{name}/perl5/%{_arch}-linux-thread-multi/auto/GD/GD.so
chrpath --delete $RPM_BUILD_ROOT%{_libdir}/%{name}/perl5/%{_arch}-linux-thread-multi/auto/DBD/mysql/mysql.so
chrpath --delete $RPM_BUILD_ROOT%{_libdir}/%{name}/perl5/%{_arch}-linux-thread-multi/auto/Time/HiRes/HiRes.so
chrpath --delete $RPM_BUILD_ROOT%{_libdir}/%{name}/perl5/%{_arch}-linux-thread-multi/auto/XML/Parser/Expat/Expat.so

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)

%files core
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{name}
%attr(755,root,root) %{_bindir}/naemonstats
%attr(755,root,root) %{_bindir}/oconfsplit
%{systemdunitdir}/%{name}.service
%{systemdtmpfilesdir}/%{name}.conf
%attr(755,root,root) %{_initrddir}/%{name}
%config(noreplace) /etc/logrotate.d/%{name}-core
%dir %{_sysconfdir}/%{name}/
%attr(2775,naemon,naemon) %dir %{_sysconfdir}/%{name}/conf.d
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.cfg
%config(noreplace) %{_sysconfdir}/%{name}/resource.cfg
%attr(664,naemon,naemon) %config(noreplace) %{_sysconfdir}/%{name}/conf.d/*.cfg
%attr(664,naemon,naemon) %config(noreplace) %{_sysconfdir}/%{name}/conf.d/templates/*.cfg
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(2775,naemon,http) %dir %{_localstatedir}/cache/%{name}/checkresults
%attr(2775,naemon,naemon) %dir %{_localstatedir}/cache/%{name}
%attr(755,naemon,naemon) %dir %{_localstatedir}/lib/%{name}
%attr(755,naemon,naemon) %dir %{_localstatedir}/log/%{name}
%attr(755,naemon,naemon) %dir %{_localstatedir}/log/%{name}/archives
%attr(-,root,root) %{_datadir}/%{name}/documentation
%attr(-,root,root) %{_libdir}/%{name}/libnaemon.so*
%attr(-,root,root) %{_libdir}/%{name}/plugins

%files devel
%defattr(644,root,root,755)
%attr(-,root,root) %{_includedir}/%{name}/
%attr(-,root,root) %{_libdir}/%{name}/libnaemon.a
%attr(-,root,root) %{_libdir}/%{name}/libnaemon.la

%files livestatus
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{name}-unixcat
%{_libdir}/%{name}/livestatus.o
%attr(755,naemon,naemon) %dir %{_localstatedir}/log/%{name}

%files thruk
%defattr(644,root,root,755)
%attr(755,root, root) %{_bindir}/thruk
%attr(755,root, root) %{_bindir}/naglint
%attr(755,root, root) %{_bindir}/nagexp
%attr(755,root, root) %{_initrddir}/thruk
%config %{_sysconfdir}/%{name}/ssi
%config %{_sysconfdir}/%{name}/thruk.conf
%attr(644,http,http) %config(noreplace) %{_sysconfdir}/%{name}/thruk_local.conf
%attr(644,http,http) %config(noreplace) %{_sysconfdir}/%{name}/cgi.cfg
%attr(644,http,http) %config(noreplace) %{_sysconfdir}/%{name}/htpasswd
%attr(755,http,http) %dir %{_sysconfdir}/%{name}/bp
%config(noreplace) %{_sysconfdir}/%{name}/naglint.conf
%config(noreplace) %{_sysconfdir}/%{name}/log4perl.conf
%config(noreplace) /etc/logrotate.d/%{name}-thruk
%config(noreplace) %{_sysconfdir}/httpd/conf.d/thruk.conf
%config(noreplace) %{_sysconfdir}/httpd/conf.d/thruk_cookie_auth_vhost.conf
%config(noreplace) %{_sysconfdir}/%{name}/themes
%config(noreplace) %{_sysconfdir}/%{name}/menu_local.conf
%attr(755,root, root) %{_datadir}/%{name}/thruk_auth
%attr(755,root, root) %{_datadir}/%{name}/script/thruk_fastcgi.pl
%attr(755,http,http) %dir %{_localstatedir}/cache/%{name}/thruk
%{_datadir}/%{name}/root
%{_datadir}/%{name}/templates
%{_datadir}/%{name}/themes
%{_datadir}/%{name}/plugins/plugins-available/business_process
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/business_process
%config %{_sysconfdir}/%{name}/plugins/plugins-available/business_process
%{_datadir}/%{name}/plugins/plugins-available/conf
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/conf
%config %{_sysconfdir}/%{name}/plugins/plugins-available/conf
%{_datadir}/%{name}/plugins/plugins-available/dashboard
%config %{_sysconfdir}/%{name}/plugins/plugins-available/dashboard
%{_datadir}/%{name}/plugins/plugins-available/minemap
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/minemap
%config %{_sysconfdir}/%{name}/plugins/plugins-available/minemap
%{_datadir}/%{name}/plugins/plugins-available/mobile
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/mobile
%config %{_sysconfdir}/%{name}/plugins/plugins-available/mobile
%{_datadir}/%{name}/plugins/plugins-available/panorama
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/panorama
%config %{_sysconfdir}/%{name}/plugins/plugins-available/panorama
%{_datadir}/%{name}/plugins/plugins-available/shinken_features
%config %{_sysconfdir}/%{name}/plugins/plugins-available/shinken_features
%{_datadir}/%{name}/plugins/plugins-available/statusmap
%config %{_sysconfdir}/%{name}/plugins/plugins-enabled/statusmap
%config %{_sysconfdir}/%{name}/plugins/plugins-available/statusmap
%{_datadir}/%{name}/plugins/plugins-available/wml
%config %{_sysconfdir}/%{name}/plugins/plugins-available/wml
%{_datadir}/%{name}/lib
%{_datadir}/%{name}/Changes
%{_datadir}/%{name}/LICENSE
%{_datadir}/%{name}/menu.conf
%{_datadir}/%{name}/dist.ini
%{_datadir}/%{name}/thruk_cookie_auth.include
%{_datadir}/%{name}/docs/THRUK_MANUAL.html
%{_datadir}/%{name}/docs/FAQ.html
%{_datadir}/%{name}/%{name}-version
%attr(755,root,root) %{_datadir}/%{name}/fcgid_env.sh
%{_mandir}/man3/nagexp.3*
%{_mandir}/man3/naglint.3*
%{_mandir}/man3/thruk.3*
%{_mandir}/man8/thruk.8*

%files thruk-libs
%defattr(644,root,root,755)
%attr(-,root,root) %{_libdir}/%{name}/perl5

%files thruk-reporting
%defattr(644,root,root,755)
%{_datadir}/%{name}/plugins/plugins-available/reports2
%{_sysconfdir}/%{name}/plugins/plugins-available/reports2
%{_sysconfdir}/%{name}/plugins/plugins-enabled/reports2
