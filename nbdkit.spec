%global _hardened_build 1

%ifarch aarch64 %{arm} %{ix86} x86_64 ppc %{power64}
%global have_libguestfs 1
%endif

# Architectures where the complete test suite must pass.
#
# On all other architectures, a simpler test suite must pass.  This
# omits any tests that run full qemu, since running qemu under TCG is
# often broken on non-x86_64 arches.
%global complete_test_arches x86_64

# Currently everything has Python 2.  RHEL 7 doesn't have Python 3.
%if 0%{?rhel} != 7
%global have_python3 1
%endif

# If we should verify tarball signature with GPGv2.
%global verify_tarball_signature 1

# If there are patches which touch autotools files, set this to 1.
%global patches_touch_autotools 1

# The source directory.
%global source_directory 1.8-stable

Name:           nbdkit
Version:        1.8.0
Release:        1%{?dist}
Summary:        NBD server

License:        BSD
URL:            https://github.com/libguestfs/nbdkit

Source0:        http://libguestfs.org/download/nbdkit/%{source_directory}/%{name}-%{version}.tar.gz
%if 0%{verify_tarball_signature}
Source1:        http://libguestfs.org/download/nbdkit/%{source_directory}/%{name}-%{version}.tar.gz.sig
# Keyring used to verify tarball signature.
Source2:       libguestfs.keyring
%endif

# Patches come from:
# https://github.com/libguestfs/nbdkit/tree/rhel-7.7

# Patches.
Patch0001:     0001-partitioning-Rename-crc32-to-efi_crc32-to-avoid-conf.patch

%if 0%{patches_touch_autotools}
BuildRequires: autoconf, automake, libtool
%endif

%if 0%{?rhel} == 7
# On RHEL 7, nothing in the virt stack is shipped on aarch64 and
# libguestfs was not shipped on POWER (fixed in 7.5).  We could in
# theory make all of this work by having lots more conditionals, but
# for now limit this package to x86_64 on RHEL.
ExclusiveArch:  x86_64
%endif

%ifnarch %{complete_test_arches}
BuildRequires:  autoconf, automake, libtool
%endif
BuildRequires:  /usr/bin/pod2man
BuildRequires:  gnutls-devel
BuildRequires:  libselinux-devel
%if 0%{?have_libguestfs}
BuildRequires:  libguestfs-devel
%endif
BuildRequires:  libvirt-devel
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
BuildRequires:  libcurl-devel
BuildRequires:  perl-devel
BuildRequires:  perl(ExtUtils::Embed)
BuildRequires:  python2-devel
%if 0%{?have_python3}
BuildRequires:  python3-devel
%endif
%ifarch %{ocaml_native_compiler}
# Requires OCaml 4.02.2 which contains fix for
# http://caml.inria.fr/mantis/view.php?id=6693
BuildRequires:  ocaml >= 4.02.2
%endif
BuildRequires:  ruby-devel
%if 0%{verify_tarball_signature}
BuildRequires: gnupg2
%endif

# Only for running the test suite:
BuildRequires:  /usr/bin/certtool
BuildRequires:  /usr/bin/qemu-img
BuildRequires:  /usr/bin/socat
BuildRequires:  /usr/sbin/ss

%description
NBD is a protocol for accessing block devices (hard disks and
disk-like things) over the network.

'nbdkit' is a toolkit for creating NBD servers.

The key features are:

* Multithreaded NBD server written in C with good performance.

* Well-documented, simple plugin API with a stable ABI guarantee.
  Allows you to export "unconventional" block devices easily.

* Liberal license (BSD) allows nbdkit to be linked to proprietary
  libraries or included in proprietary code.

You probably want to install one of more plugins (%{name}-plugin-*).

To develop plugins, install the %{name}-devel package and start by
reading the nbdkit(1) and nbdkit-plugin(3) manual pages.


%package basic-plugins
Summary:        Basic plugins for %{name}
License:        BSD

Requires:       %{name}%{?_isa} = %{version}-%{release}

# For upgrade path, remove these in Fedora 30.
Obsoletes:      %{name}-plugin-file < 1.1.19-1
Obsoletes:      %{name}-plugin-nbd < 1.1.19-1
Obsoletes:      %{name}-plugin-streaming < 1.1.19-1


%description basic-plugins
This package contains some basic plugins for %{name} which have only
trivial dependencies.

nbdkit-data-plugin         Serve small amounts of data from the command line.

nbdkit-file-plugin         The normal file plugin for serving files.

nbdkit-memory-plugin       A virtual memory plugin.

nbdkit-nbd-plugin          An NBD forwarding plugin.

nbdkit-null-plugin         A null (bitbucket) plugin.

nbdkit-pattern-plugin      Fixed test pattern.

nbdkit-partitioning-plugin Create virtual disks from partitions.

nbdkit-random-plugin       Random content plugin for testing.

nbdkit-split-plugin        Concatenate one or more files.

nbdkit-streaming-plugin    A streaming file serving plugin.

nbdkit-zero-plugin         Zero-length plugin for testing.


%package example-plugins
Summary:        Example plugins for %{name}
License:        BSD

Requires:       %{name}%{?_isa} = %{version}-%{release}

# For upgrade path, remove this in Fedora 30.
Obsoletes:      %{name}-plugin-examples < 1.1.19-1


%description example-plugins
This package contains example plugins for %{name}.


# The plugins below have non-trivial dependencies are so are
# packaged separately.

%package plugin-python-common
Summary:        Python 2 and 3 plugin common files for %{name}
License:        BSD

Requires:       %{name}%{?_isa} = %{version}-%{release}


%description plugin-python-common
This package contains common files shared between Python 2
and Python 3 %{name} plugins.

You should not install this package directly.  Instead install
either %{name}-plugin-python2 or %{name}-plugin-python3.


%package plugin-python2
Summary:        Python 2 plugin for %{name}
License:        BSD

Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-plugin-python-common = %{version}-%{release}


%description plugin-python2
This package lets you write Python 2 plugins for %{name}.


%ifarch %{ix86} x86_64
%package plugin-vddk
Summary:        VMware VDDK plugin for %{name}
License:        BSD

Requires:       %{name}%{?_isa} = %{version}-%{release}


%description plugin-vddk
This package is a plugin for %{name} which connects to
VMware VDDK for accessing VMware disks and servers.
%endif


%package devel
Summary:        Development files and documentation for %{name}
License:        BSD

Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig


%description devel
This package contains development files and documentation
for %{name}.  Install this package if you want to develop
plugins for %{name}.


%prep
%if 0%{verify_tarball_signature}
tmphome="$(mktemp -d)"
gpgv2 --homedir "$tmphome" --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}
%endif
%autosetup -p1
%if 0%{patches_touch_autotools}
autoreconf -i
%endif

%ifnarch %{complete_test_arches}
# Simplify the test suite so it doesn't require qemu.
sed -i -e '/^if HAVE_LIBGUESTFS/,/^endif HAVE_LIBGUESTFS/d' tests/Makefile.am
sed -i -e '/^if HAVE_GUESTFISH/,/^endif HAVE_GUESTFISH/d' tests/Makefile.am
automake
%endif

# Ancient qemu-io in RHEL 7 doesn't support -f FORMAT option.  However
# we can just omit it and the tests still work fine.
for f in tests/*.sh; do
  sed -i -e 's/qemu-io -f raw/qemu-io/g' \
         -e 's/qemu-io -r -f raw/qemu-io -r/g' $f
done

# Disable numerous tests which cannot work with ancient gnutls or
# qemu-img on RHEL 7.
for f in tests/test-cache.sh \
         tests/test-cow.sh \
         tests/test-data-7E.sh \
         tests/test-data-file.sh \
         tests/test-data-raw.sh \
         tests/test-floppy.sh \
         tests/test-fua.sh \
         tests/test-iso.sh \
         tests/test-log.sh \
         tests/test-memory-largest-for-qemu.sh \
         tests/test-nozero.sh \
         tests/test-offset2.sh \
         tests/test-parallel-file.sh \
         tests/test-parallel-nbd.sh \
         tests/test-partitioning2.sh \
         tests/test-partitioning3.sh \
         tests/test-pattern.sh \
         tests/test-pattern-largest-for-qemu.sh \
         tests/test-truncate1.sh \
         tests/test-truncate2.sh ; do
    rm $f
    touch $f
    chmod +x $f
done

# Patch doesn't set permissions correctly. XXX
chmod +x tests/test-vddk.sh


%build
# Force immediate binding for hardened build for plugins.
# https://bugzilla.redhat.com/show_bug.cgi?id=977446#c13
export LDFLAGS="$LDFLAGS -Wl,-z,now"

# Build for Python 3 in a separate subdirectory.  Upstream does not
# support srcdir!=builddir so copy the whole source.
copy="$(mktemp -d)"
cp -a . "$copy"
mv "$copy" python3

%configure --disable-static --with-tls-priority=NORMAL \
	--disable-lua \
	--disable-perl \
	--disable-ocaml \
	--disable-ruby \
	--without-curl \
	--without-libvirt \
	--without-zlib \
	--without-liblzma \
	--without-libguestfs
make %{?_smp_mflags}

%if 0%{?have_python3}
pushd python3
export PYTHON=%{_bindir}/python3
%configure --disable-static --disable-lua --disable-perl --disable-ocaml --disable-ruby
# Verify that it picked the correct version of Python
# to avoid RHBZ#1404631 happening again silently.
grep '^PYTHON_VERSION = 3' Makefile
make %{?_smp_mflags}
unset PYTHON
popd
%endif


%install
%make_install

pushd $RPM_BUILD_ROOT%{_libdir}/nbdkit/plugins/
mv nbdkit-python-plugin.so nbdkit-python2-plugin.so
# For backwards compatibility, "the" python plugin is Python 2.
# Probably we will change this in future if Fedora switches
# exclusively to Python 3.
ln -s nbdkit-python2-plugin.so nbdkit-python-plugin.so
popd

# Disable built-in filters but leave the empty directory.
rm -r $RPM_BUILD_ROOT%{_libdir}/%{name}/filters/nbdkit-*-filter.so
rm -r $RPM_BUILD_ROOT%{_mandir}/man1/nbdkit-*-filter.1*

# Delete libtool crap.
find $RPM_BUILD_ROOT -name '*.la' -delete

# Delete the VDDK plugin on !x86 architectures since it is not
# applicable there.
%ifnarch %{ix86} x86_64
rm $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins/nbdkit-vddk-plugin.so
rm $RPM_BUILD_ROOT%{_mandir}/man1/nbdkit-vddk-plugin.1*
%endif

# Remove bash-completion (if it was built) because we don't want to
# support it.
rm -rf $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d

# Remove some basic plugins which we don't want to support.  We may
# add these back later if there is customer demand.
rm $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins/nbdkit-floppy-plugin.so
rm $RPM_BUILD_ROOT%{_mandir}/man1/nbdkit-floppy-plugin.1*
rm $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins/nbdkit-iso-plugin.so
rm $RPM_BUILD_ROOT%{_mandir}/man1/nbdkit-iso-plugin.1*
rm $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins/nbdkit-sh-plugin.so
rm $RPM_BUILD_ROOT%{_mandir}/man3/nbdkit-sh-plugin.3*


%check
# Workaround for broken libvirt (RHBZ#1138604).
mkdir -p $HOME/.cache/libvirt

# Make sure we can see the debug messages (RHBZ#1230160).
export LIBGUESTFS_DEBUG=1
export LIBGUESTFS_TRACE=1

make check -j1 || {
    cat tests/test-suite.log
    exit 1
  }


%files
%doc README
%license LICENSE
%{_sbindir}/nbdkit
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/plugins
%dir %{_libdir}/%{name}/filters
%{_mandir}/man1/nbdkit.1*


%files basic-plugins
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-data-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-file-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-memory-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-nbd-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-null-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-partitioning-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-pattern-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-random-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-split-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-streaming-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-zero-plugin.so
%{_mandir}/man1/nbdkit-data-plugin.1*
%{_mandir}/man1/nbdkit-file-plugin.1*
%{_mandir}/man1/nbdkit-memory-plugin.1*
%{_mandir}/man1/nbdkit-nbd-plugin.1*
%{_mandir}/man1/nbdkit-null-plugin.1*
%{_mandir}/man1/nbdkit-partitioning-plugin.1*
%{_mandir}/man1/nbdkit-pattern-plugin.1*
%{_mandir}/man1/nbdkit-random-plugin.1*
%{_mandir}/man1/nbdkit-split-plugin.1*
%{_mandir}/man1/nbdkit-streaming-plugin.1*
%{_mandir}/man1/nbdkit-zero-plugin.1*


%files example-plugins
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-example*-plugin.so
%{_mandir}/man1/nbdkit-example*-plugin.1*


%files plugin-python-common
%doc README
%license LICENSE
%{_mandir}/man3/nbdkit-python-plugin.3*


%files plugin-python2
%{_libdir}/%{name}/plugins/nbdkit-python-plugin.so
%{_libdir}/%{name}/plugins/nbdkit-python2-plugin.so


%ifarch %{ix86} x86_64
%files plugin-vddk
%doc README
%license LICENSE
%{_libdir}/%{name}/plugins/nbdkit-vddk-plugin.so
%{_mandir}/man1/nbdkit-vddk-plugin.1*
%endif


%files devel
%doc OTHER_PLUGINS README TODO
%license LICENSE
# Include the source of the example plugins in the documentation.
%doc plugins/example*/*.c
#%doc plugins/example4/nbdkit-example4-plugin
#%doc plugins/perl/example.pl
#%doc plugins/python/example.py
#%doc plugins/ruby/example.rb
%{_includedir}/nbdkit-common.h
%{_includedir}/nbdkit-filter.h
%{_includedir}/nbdkit-plugin.h
%{_mandir}/man1/nbdkit-captive.1*
%{_mandir}/man3/nbdkit-filter.3*
%{_mandir}/man3/nbdkit-plugin.3*
%{_mandir}/man1/nbdkit-probing.1*
%{_mandir}/man1/nbdkit-protocol.1*
%{_mandir}/man1/nbdkit-service.1*
%{_mandir}/man1/nbdkit-tls.1*
%{_libdir}/pkgconfig/nbdkit.pc


%changelog
* Tue Nov 13 2018 Richard W.M. Jones <rjones@redhat.com> - 1.8.0-1
- Rebase to upstream stable version 1.8.0.
  resolves: rhbz#1621894

* Thu Nov 08 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.6-1.el7_6.2
- Enhanced Python error reporting.
  resolves: rhbz#1613946

* Fri Oct 12 2018 Pino Toscano <ptoscano@redhat.com> - 1.2.6-1.el7_6.1
- Fix TLS priority. (RHBZ#1632220)

* Wed Aug  1 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.6-1
- New stable version 1.2.6.

* Wed Jul 25 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.5-1
- New stable version 1.2.5.
- Enable VDDK plugin on x86-64 only.
- Small refactorings in the spec file.

* Sun Jul  1 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.4-4
- Add all upstream patches since 1.2.4 was released.

* Thu Jun 14 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.4-3
- Fix use of autopatch/autosetup macros in prep section.

* Tue Jun 12 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.4-2
- Add all upstream patches since 1.2.4 was released.
- Drop example4 and tar plugins since they depend on Perl.

* Sat Jun  9 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.4-1
- New stable version 1.2.4.
- Remove upstream patches.
- Enable tarball signatures.
- Add upstream patch to fix tests when guestfish not available.

* Wed Jun  6 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.3-1
- New stable version 1.2.3.
- Add patch to work around libvirt problem with relative socket paths.
- Add patch to fix the xz plugin test with recent guestfish.
- Fix version in VDDK plugin spec file.

* Sat Apr 21 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.2-1
- New stable version 1.2.2.

* Fri Apr 20 2018 Tomáš Golembiovský <tgolembi@redhat.com> - 1.2.1-2
- Fix link to sources

* Mon Apr  9 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.1-1
- New stable version 1.2.1.

* Fri Apr  6 2018 Richard W.M. Jones <rjones@redhat.com> - 1.2.0-1
- Move to stable branch version 1.2.0.
- Escape macros in %%changelog
- Run a simplified test suite on all arches.

* Thu Mar 15 2018 Tomáš Golembiovský <tgolembi@redhat.com> - 1.1.26-2
- Enable python2 plugin.

* Sat Dec 23 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.26-1
- New upstream version 1.1.26.
- Add new pkg-config file and dependency.

* Wed Dec 06 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.25-1
- New upstream version 1.1.25.

* Tue Dec 05 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.24-1
- New upstream version 1.1.24.
- Add tar plugin (new subpackage nbdkit-plugin-tar).

* Tue Dec 05 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.23-1
- New upstream version 1.1.23.
- Add example4 plugin.
- Python3 tests require libguestfs so disable on s390x.

* Sun Dec 03 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.22-1
- New upstream version 1.1.22.
- Enable tests on Fedora.

* Sat Dec 02 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.20-1
- New upstream version 1.1.20.
- Add nbdkit-split-plugin to basic plugins.

* Sat Dec 02 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.19-2
- OCaml 4.06.0 rebuild.

* Thu Nov 30 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.19-1
- New upstream version 1.1.19.
- Combine all the simple plugins in %%{name}-basic-plugins.
- Add memory and null plugins.
- Rename the example plugins subpackage.
- Use %%license instead of %%doc for license file.
- Remove patches now upstream.

* Wed Nov 29 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.18-4
- Fix Python 3 builds / RHEL macros (RHBZ#1404631).

* Tue Nov 21 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.18-3
- New upstream version 1.1.18.
- Add NBD forwarding plugin.
- Add libselinux-devel so that SELinux support is enabled in the daemon.
- Apply all patches from upstream since 1.1.18.

* Fri Oct 20 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.16-2
- New upstream version 1.1.16.
- Disable python3 plugin on RHEL/EPEL <= 7.
- Only ship on x86_64 in RHEL/EPEL <= 7.

* Wed Sep 27 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.15-1
- New upstream version 1.1.15.
- Enable TLS support.

* Fri Sep 01 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.14-1
- New upstream version 1.1.14.

* Fri Aug 25 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.13-1
- New upstream version 1.1.13.
- Remove patches which are all upstream.
- Remove grubby hack, should not be needed with modern supermin.

* Sat Aug 19 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-13
- Rebuild for OCaml 4.05.0.

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.12-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.12-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jun 27 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-10
- Rebuild for OCaml 4.04.2.

* Sun Jun 04 2017 Jitka Plesnikova <jplesnik@redhat.com> - 1.1.12-9
- Perl 5.26 rebuild

* Mon May 15 2017 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-8
- Rebuild for OCaml 4.04.1.

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.12-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Vít Ondruch <vondruch@redhat.com> - 1.1.12-6
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.4

* Fri Dec 23 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-5
- Rebuild for Python 3.6 update.

* Wed Dec 14 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-4
- Fix python3 subpackage so it really uses python3 (RHBZ#1404631).

* Sat Nov 05 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-3
- Rebuild for OCaml 4.04.0.

* Mon Oct 03 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-2
- Compile Python 2 and Python 3 versions of the plugin.

* Wed Jun 08 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.12-1
- New upstream version 1.1.12
- Enable Ruby plugin.
- Disable tests on Rawhide because libvirt is broken again (RHBZ#1344016).

* Wed May 25 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-10
- Add another upstream patch since 1.1.11.

* Mon May 23 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-9
- Add all patches upstream since 1.1.11 (fixes RHBZ#1336758).

* Tue May 17 2016 Jitka Plesnikova <jplesnik@redhat.com> - 1.1.11-7
- Perl 5.24 rebuild

* Wed Mar 09 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-6
- When tests fail, dump out test-suite.log so we can debug it.

* Fri Feb 05 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-5
- Don't run tests on x86, because kernel is broken there
  (https://bugzilla.redhat.com/show_bug.cgi?id=1302071)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.11-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Jan 11 2016 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-3
- Add support for newstyle NBD protocol (RHBZ#1297100).

* Sat Oct 31 2015 Richard W.M. Jones <rjones@redhat.com> - 1.1.11-1
- New upstream version 1.1.11.

* Thu Jul 30 2015 Richard W.M. Jones <rjones@redhat.com> - 1.1.10-3
- OCaml 4.02.3 rebuild.

* Sat Jun 20 2015 Richard W.M. Jones <rjones@redhat.com> - 1.1.10-2
- Enable libguestfs plugin on aarch64.

* Fri Jun 19 2015 Richard W.M. Jones <rjones@redhat.com> - 1.1.10-1
- New upstream version.
- Enable now working OCaml plugin (requires OCaml >= 4.02.2).

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.9-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 11 2015 Jitka Plesnikova <jplesnik@redhat.com> - 1.1.9-5
- Perl 5.22 rebuild

* Wed Jun 10 2015 Richard W.M. Jones <rjones@redhat.com> - 1.1.9-4
- Enable debugging messages when running make check.

* Sat Jun 06 2015 Jitka Plesnikova <jplesnik@redhat.com> - 1.1.9-3
- Perl 5.22 rebuild

* Tue Oct 14 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.9-2
- New upstream version 1.1.9.
- Add the streaming plugin.
- Include fix for streaming plugin in 1.1.9.

* Wed Sep 10 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.8-4
- Rebuild for updated Perl in Rawhide.
- Workaround for broken libvirt (RHBZ#1138604).

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 21 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.8-1
- New upstream version 1.1.8.
- Add support for cURL, and new nbdkit-plugin-curl package.

* Fri Jun 20 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.7-1
- New upstream version 1.1.7.
- Remove patches which are now all upstream.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.6-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Mar 06 2014 Dan Horák <dan[at]danny.cz> - 1.1.6-4
- libguestfs is available only on selected arches

* Fri Feb 21 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.6-3
- Backport some upstream patches, fixing a minor bug and adding more tests.
- Enable the tests since kernel bug is fixed.

* Sun Feb 16 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.6-1
- New upstream version 1.1.6.

* Sat Feb 15 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.5-2
- New upstream version 1.1.5.
- Enable the new Python plugin.
- Perl plugin man page moved to section 3.
- Perl now requires ExtUtils::Embed.

* Mon Feb 10 2014 Richard W.M. Jones <rjones@redhat.com> - 1.1.4-1
- New upstream version 1.1.4.
- Enable the new Perl plugin.

* Sun Aug  4 2013 Richard W.M. Jones <rjones@redhat.com> - 1.1.3-1
- New upstream version 1.1.3 which fixes some test problems.
- Disable tests because Rawhide kernel is broken (RHBZ#991808).
- Remove a single quote from description which confused emacs.
- Remove patch, now upstream.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun Jul 21 2013 Richard W.M. Jones <rjones@redhat.com> - 1.1.2-3
- Fix segfault when IPv6 client is used (RHBZ#986601).

* Tue Jul 16 2013 Richard W.M. Jones <rjones@redhat.com> - 1.1.2-2
- New development version 1.1.2.
- Disable the tests on Fedora <= 18.

* Tue Jun 25 2013 Richard W.M. Jones <rjones@redhat.com> - 1.1.1-1
- New development version 1.1.1.
- Add libguestfs plugin.
- Run the test suite.

* Mon Jun 24 2013 Richard W.M. Jones <rjones@redhat.com> - 1.0.0-4
- Initial release.
