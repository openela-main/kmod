Name:		kmod
Version:	25
Release:	19%{?dist}
Summary:	Linux kernel module management utilities

Group:		System Environment/Kernel
License:	GPLv2+
URL:		http://git.kernel.org/?p=utils/kernel/kmod/kmod.git;a=summary
Source0:	https://www.kernel.org/pub/linux/utils/kernel/kmod/%{name}-%{version}.tar.xz
Source1:	weak-modules
Source2:	depmod.conf.dist
Exclusiveos:	Linux

Patch01:	kmod-signature-do-not-report-wrong-data-for-pkc-7-signatu.patch
Patch02:	kmod-libkmod-signature-implement-pkcs7-parsing-with-opens.patch
Patch03:	kmod-modprobe-ignore-builtin-module-on-recursive-removing.patch
Patch04:	0001-depmod-prevent-module-dependency-files-missing-durin.patch
Patch05:	0002-depmod-prevent-module-dependency-files-corruption-du.patch

BuildRoot:     %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:	chrpath
BuildRequires:	zlib-devel
BuildRequires:	xz-devel
BuildRequires:  libxslt
BuildRequires:  openssl-devel
# Remove it as soon as no need for Patch02 anymore (Makefile.am updated)
BuildRequires:  automake autoconf libtool

Provides:	module-init-tools = 4.0-1
Obsoletes:	module-init-tools < 4.0-1
Provides:	/sbin/modprobe

%description
The kmod package provides various programs needed for automatic
loading and unloading of modules under 2.6, 3.x, and later kernels, as well
as other module management programs. Device drivers and filesystems are two
examples of loaded and unloaded modules.

%package libs
Summary:	Libraries to handle kernel module loading and unloading
License:	LGPLv2+
Group:		System Environment/Libraries

%description libs
The kmod-libs package provides runtime libraries for any application that
wishes to load or unload Linux kernel modules from the running system.

%package devel
Summary:	Header files for kmod development
Group:		Development/Libraries
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

%description devel
The kmod-devel package provides header files used for development of
applications that wish to load or unload Linux kernel modules.

%prep
%setup -q
%patch01 -p1
%patch02 -p1
%patch03 -p1
%patch04 -p1
%patch05 -p1

%build
export V=1
aclocal
autoreconf --install --symlink
%configure \
  --with-zlib \
  --with-xz   \
  --with-openssl
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
pushd $RPM_BUILD_ROOT/%{_mandir}/man5
ln -s modprobe.d.5.gz modprobe.conf.5.gz
popd

rm -rf $RPM_BUILD_ROOT%{_libdir}/*.la
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
ln -sf ../bin/kmod $RPM_BUILD_ROOT%{_sbindir}/modprobe
ln -sf ../bin/kmod $RPM_BUILD_ROOT%{_sbindir}/modinfo
ln -sf ../bin/kmod $RPM_BUILD_ROOT%{_sbindir}/insmod
ln -sf ../bin/kmod $RPM_BUILD_ROOT%{_sbindir}/rmmod
ln -sf ../bin/kmod $RPM_BUILD_ROOT%{_sbindir}/depmod
ln -sf ../bin/kmod $RPM_BUILD_ROOT%{_sbindir}/lsmod

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/depmod.d
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/modprobe.d

mkdir -p $RPM_BUILD_ROOT/sbin
install -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_sbindir}/weak-modules
install -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/depmod.d/dist.conf

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%dir %{_sysconfdir}/depmod.d
%dir %{_sysconfdir}/modprobe.d
%dir %{_prefix}/lib/modprobe.d
%{_bindir}/kmod
%{_sbindir}/modprobe
%{_sbindir}/modinfo
%{_sbindir}/insmod
%{_sbindir}/rmmod
%{_sbindir}/lsmod
%{_sbindir}/depmod
%{_sbindir}/weak-modules
%{_datadir}/bash-completion/
%{_sysconfdir}/depmod.d/dist.conf
%attr(0644,root,root) %{_mandir}/man5/*.5*
%attr(0644,root,root) %{_mandir}/man8/*.8*
%doc NEWS README TODO

%files libs
%{!?_licensedir:%global license %%doc}
%license COPYING
%{_libdir}/libkmod.so.*

%files devel
%{_includedir}/libkmod.h
%{_libdir}/pkgconfig/libkmod.pc
%{_libdir}/libkmod.so

%changelog
* Mon Nov 29 2021 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-19
- depmod: fix parallel execution issues
  Resolves: rhbz#2026938

* Fri Apr 16 2021 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-18
- weak-modules: do not require dracut wneh using --no-initramfs
  Resolves: rhbz#1935416

* Fri Dec 18 2020 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-17
- weak-modules: reset compatible_modules if configuration is not valid
  Resolves: rhbz#1907855

* Mon Dec  9 2019 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-16
- weak-modules: update_modules_for_krel: always finish sandbox
- weak-modules: groupping: use dependencies of extra/ provider
  Resolves: rhbz#1778889

* Mon Dec  9 2019 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-15
- weak-modules: reverse checking order for add-kernel
  Resolves: rhbz#1755196

* Mon Dec  2 2019 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-14
- modprobe: do not fail on built-in modules
  Resolves: rhbz#1767513

* Tue Apr 16 2019 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-13
- weak-modules: handle independent modules in one run
  Resolves: rhbz#1695763

* Tue Apr  2 2019 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-12
- weak-modules: use asterisk for kernel version in sandbox
  Resolves: rhbz#1689052

* Tue Feb  5 2019 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-11
- add PKCS7/openssl support.
  Resolves: rhbz#1668459.

* Tue Dec 11 2018 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-10
- weak-modules: group modules on add-kernel
- weak-modules: do not make groups if there are no extra modules
  Resolves: rhbz#1649211

* Tue Oct  2 2018 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-9
- Rebuild with updated flags.
  Resolves: rhbz#1630574.

* Tue Sep  4 2018 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-8
- weak-modules: fix initial state creation for dry-run
- weak-modules: check compatibility in a temporary directory
  Resolves: rhbz#1622990.

* Tue Aug 28 2018 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-7
- weak-modules: use is_kernel_installed wrapper in update_modules_for_krel.
- weak-modules: more abstract symvers search implementation.
- weak-modules: use additional paths for System.map file.
  Resolves: rhbz#1621306.

* Thu Aug 09 2018 Eugene Syromiatnikov <esyr@redhat.com> - 25-6
- weak-modules: check also for /lib/modules/$krel/symvers.gz as a possible
  symvers file path.
  Resolves: rhbz#1614119.

* Mon Jul 30 2018 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-5
- weak-modules: handle versions with + and other special regex symbols
- weak-modules: fix misleading message when cannot find dracut.
  Resolves: rhbz#1609372.

* Fri Jul 27 2018 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-4
- fix dracut path, /usr/bin/dracut

* Wed Jul 25 2018 Yauheni Kaliuta <ykaliuta@redhat.com> - 25-3
- Add depmod.d/dist.conf.
- Update weak-modules to RHEL version.

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 25-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 09 2018 Josh Boyer <jwboyer@fedoraproject.org> - 25-1
- Update to version 25 (rhbz 1532597)

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 24-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 24-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 24 2017 Josh Boyer <jwboyer@fedoraproject.org> - 24-1
- Update to version 24 (rhbz 1426589)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 23-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jul 22 2016 Josh Boyer <jwboyer@fedoraproject.org> - 23-1
- Update to version 23

* Thu Feb 25 2016 Peter Robinson <pbrobinson@fedoraproject.org> 22-4
- Add powerpc patch to fix ToC on 4.5 ppc64le kernel

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 22-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 07 2016 Josh Boyer <jwboyer@fedoraproject.org> - 22-2
- Fix path to dracut in weak-modules (rhbz 1295038)

* Wed Nov 18 2015 Josh Boyer <jwboyer@fedoraproject.org> - 22-1
- Update to version 22

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 21-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 15 2015 Ville Skyttä <ville.skytta@iki.fi> - 21-2
- Own bash completion dirs not owned by anything in dep chain

* Tue Jun 09 2015 Josh Boyer <jwboyer@fedoraproject.org> - 21-1
- Update to verion 21

* Mon Mar 02 2015 Josh Boyer <jwboyer@fedoraproject.org> - 20.1
- Update to version 20

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 19-2
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Sun Nov 16 2014 Josh Boyer <jwboyer@fedoraproject.org> - 19-1
- Update to version 19

* Wed Oct 29 2014 Josh Boyer <jwboyer@fedoraproject.org> - 18-4
- Backport patch to fix device node permissions (rhbz 1147248)

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 18-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jul 12 2014 Tom Callaway <spot@fedoraproject.org> - 18-2
- fix license handling

* Tue Jun 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 18-1
- Update to version 18

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 17-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Apr 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 17-1
- Update to version 17

* Thu Jan 02 2014 Václav Pavlín <vpavlin@redhat.com> - 16-1
- Update to version 16

* Thu Aug 22 2013 Josh Boyer <jwboyer@fedoraproject.org> - 15-1
- Update to version 15

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 14-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jul 05 2013 Josh Boyer <jwboyer@redhat.com> - 14-1
- Update to version 14

* Fri Apr 19 2013 Václav Pavlín <vpavlin@redhat.com> - 13-2
- Main package should require -libs

* Wed Apr 10 2013 Josh Boyer <jwboyer@redhat.com> - 13-1
- Update to version 13

* Wed Mar 20 2013 Weiping Pan <wpan@redhat.com> - 12-3
- Pull in weak-modules for kABI from Jon Masters <jcm@redhat.com>

* Mon Mar 18 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to make rmmod understand built-in modules (rhbz 922187)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Dec 06 2012 Josh Boyer <jwboyer@redhat.com>
- Update to version 12

* Thu Nov 08 2012 Josh Boyer <jwboyer@redhat.com>
- Update to version 11

* Fri Sep 07 2012 Josh Boyer <jwboyer@redaht.com>
- Update to version 10

* Mon Aug 27 2012 Josh Boyer <jwboyer@redhat.com>
- Update to version 9

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May 23 2012 Josh Boyer <jwboyer@redhat.com> - 8-2
- Provide modprobe.conf(5) (rhbz 824552)

* Tue May 08 2012 Josh Boyer <jwboyer@redhat.com> - 8-1
- Update to version 8

* Mon Mar 19 2012 Kay Sievers <kay@redhat.com> - 7-1
- update to version 7
  - fix issue with --show-depends, where built-in
    modules of the running kernel fail to include
    loadable modules of the kernel specified

* Sun Mar 04 2012 Kay Sievers <kay@redhat.com> - 6-1
- update to version 6
- remove all patches, they are included in the release

* Fri Feb 24 2012 Kay Sievers <kay@redhat.com> - 5-8
- try to address brc#771285

* Sun Feb 12 2012 Kay Sievers <kay@redhat.com> - 5-7
- fix infinite loop with softdeps

* Thu Feb 09 2012 Harald Hoyer <harald@redhat.com> 5-6
- add upstream patch to fix "modprobe --ignore-install --show-depends"
  otherwise dracut misses a lot of modules, which are already loaded

* Wed Feb 08 2012 Harald Hoyer <harald@redhat.com> 5-5
- add "lsmod"

* Tue Feb  7 2012 Kay Sievers <kay@redhat.com> - 5-4
- remove temporarily added fake-provides

* Tue Feb  7 2012 Kay Sievers <kay@redhat.com> - 5-3
- temporarily add fake-provides to be able to bootstrap
  the new udev which pulls the old udev into the buildroot

* Tue Feb  7 2012 Kay Sievers <kay@redhat.com> - 5-1
- Update to version 5
- replace the module-init-tools package and provide all tools
  as compatibility symlinks

* Mon Jan 16 2012 Kay Sievers <kay@redhat.com> - 4-1
- Update to version 4
- set --with-rootprefix=
- enable zlib and xz support

* Thu Jan 05 2012 Jon Masters <jcm@jonmasters.org> - 3-1
- Update to latest upstream (adds new depmod replacement utility)
- For the moment, use the "kmod" utility to test the various functions

* Fri Dec 23 2011 Jon Masters <jcm@jonmasters.org> - 2-6
- Update kmod-2-with-rootlibdir patch with rebuild automake files

* Fri Dec 23 2011 Jon Masters <jcm@jonmasters.org> - 2-5
- Initial build for Fedora following package import

* Thu Dec 22 2011 Jon Masters <jcm@jonmasters.org> - 2-4
- There is no generic macro for non-multilib "/lib", hardcode like others

* Thu Dec 22 2011 Jon Masters <jcm@jonmasters.org> - 2-3
- Update package incorporating fixes from initial review feedback
- Cleaups to SPEC, rpath, documentation, library and binary locations

* Thu Dec 22 2011 Jon Masters <jcm@jonmasters.org> - 2-2
- Update package for posting to wider test audience (initial review submitted)

* Thu Dec 22 2011 Jon Masters <jcm@jonmasters.org> - 2-1
- Initial Fedora package for module-init-tools replacement (kmod) library
